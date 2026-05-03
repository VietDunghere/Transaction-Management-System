from __future__ import annotations
"""
Service: TransactionService (ERD v2)
Simplified: no RiskScoringResult, TxnState, TxnStateHistory, TxnIdempotency, SuppressionRule.
fraud_score + model_version stored directly on Transaction.
"""

import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional


def _json_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.scoring import AuditLog
from app.models.transaction import Transaction
from app.repositories.analyst_repo import ModelConfigRepository
from app.repositories.transaction_repo import TransactionRepository
from app.repositories.velocity_repo import CustomerRepository, MerchantRepository, VelocityRepository
from app.schemas.transaction import TransactionSubmitRequest, TransactionSubmitResponse
from app.services.fraud_scoring_service import FraudScoringInput, FraudScoringService
from app.models.user import User
from app.utils.card import hash_card_number, mask_card_number

logger = get_logger(__name__)


class TransactionService:

    def __init__(self, db: Session) -> None:
        self._db = db
        self._txn_repo = TransactionRepository(db)
        self._customer_repo = CustomerRepository(db)
        self._merchant_repo = MerchantRepository(db)
        self._velocity_repo = VelocityRepository(db)
        self._config_repo = ModelConfigRepository(db)
        self._scoring_svc = FraudScoringService.get_instance()

    def submit(
        self,
        request: TransactionSubmitRequest,
        submitted_by_user_id: str,
    ) -> TransactionSubmitResponse:
        # ---- Load entities ----
        customer = self._customer_repo.get_by_id(request.customer_id)
        if customer is None:
            raise NotFoundError("Customer")

        merchant = self._merchant_repo.get_by_id(request.merchant_id)
        if merchant is None:
            raise NotFoundError("Merchant")

        # ---- Hash card number ----
        card_hash = hash_card_number(request.card_number)
        card_masked = mask_card_number(request.card_number)

        # ---- Update velocity stats ----
        txn_date_str = request.txn_time.strftime("%Y-%m-%d")
        velocity = self._velocity_repo.upsert(card_hash, float(request.amount), txn_date_str)

        # ---- Build scoring input ----
        scoring_input = FraudScoringInput(
            amount=float(request.amount),
            txn_time=request.txn_time,
            category=merchant.merchant_category or "misc_net",
            merchant_name=merchant.merchant_name,
            gender=customer.gender or "M",
            job=customer.job or "unknown",
            city=customer.city or "unknown",
            state=customer.city or "unknown",
            city_population=50000,
            date_of_birth=datetime.combine(customer.date_of_birth, datetime.min.time())
            if customer.date_of_birth else datetime(1980, 1, 1),
            customer_lat=float(customer.latitude or 0.0),
            customer_lon=float(customer.longitude or 0.0),
            merchant_lat=float(merchant.latitude or 0.0),
            merchant_lon=float(merchant.longitude or 0.0),
            cc_avg_daily_txn=float(velocity.avg_daily_txn),
            cc_total_txn=velocity.total_txn,
            cc_avg_amt=float(velocity.avg_amt),
            cc_std_amt=float(velocity.std_amt),
        )

        # ---- Score ----
        reject_cfg = self._config_repo.get("fraud", "reject_threshold")
        review_cfg = self._config_repo.get("fraud", "review_threshold")
        scoring_result = self._scoring_svc.score(
            scoring_input,
            reject_threshold=float(reject_cfg.param_value) if reject_cfg else None,
            review_threshold=float(review_cfg.param_value) if review_cfg else None,
        )
        logger.info(
            "fraud_scored",
            customer_id=request.customer_id,
            fraud_score=scoring_result.fraud_score,
            decision=scoring_result.decision,
        )

        # ---- Save Transaction (fraud_score + model_version inline) ----
        txn = Transaction(
            txn_id=str(uuid.uuid4()),
            customer_id=request.customer_id,
            merchant_id=request.merchant_id,
            channel_id=request.channel_id,
            submitted_by=submitted_by_user_id,
            card_number_masked=card_masked,
            card_number_hash=card_hash,
            amount=request.amount,
            txn_time=request.txn_time,
            status=scoring_result.decision,
            fraud_score=scoring_result.fraud_score,
            model_version=scoring_result.model_version,
        )
        self._txn_repo.create(txn)

        # ---- ReviewCase created by Oracle trigger TRG_AUTO_CREATE_CASE ----
        # Do NOT create ReviewCase in Python — the trigger handles it
        # on INSERT when status = 'MANUAL_REVIEW'.
        case_id = None

        # ---- Audit log ----
        actor_user = self._db.query(User.full_name).filter(User.user_id == submitted_by_user_id).first()
        audit = AuditLog(
            log_id=str(uuid.uuid4()),
            event_type="TRANSACTION_SUBMITTED",
            entity_type="Transaction",
            entity_id=txn.txn_id,
            actor_user_id=submitted_by_user_id,
            actor_name=actor_user.full_name if actor_user else None,
            detail_json=json.dumps({
                "amount": float(request.amount),
                "fraud_score": scoring_result.fraud_score,
                "decision": scoring_result.decision,
            }, default=_json_default),
        )
        self._db.add(audit)

        # ---- Commit ----
        self._db.commit()
        self._db.refresh(txn)

        return TransactionSubmitResponse(
            txn_id=txn.txn_id,
            status=scoring_result.decision,
            fraud_score=scoring_result.fraud_score,
            decision=scoring_result.decision,
            amount=txn.amount,
            created_at=txn.created_at,
            message=self._decision_message(scoring_result.decision),
            case_id=case_id,
        )

    def get_transaction(self, txn_id: str) -> Transaction:
        txn = self._txn_repo.get_by_id(txn_id)
        if txn is None:
            raise NotFoundError("Transaction")
        return txn

    def list_transactions(self, **kwargs) -> tuple[list[Transaction], int]:
        return self._txn_repo.list_transactions(**kwargs)

    @staticmethod
    def _decision_message(decision: str) -> str:
        messages = {
            "APPROVED": "Giao dịch đã được chấp thuận.",
            "REJECTED": "Giao dịch bị từ chối do nghi ngờ gian lận.",
            "MANUAL_REVIEW": "Giao dịch đang chờ xem xét thủ công.",
        }
        return messages.get(decision, "Đã xử lý.")
