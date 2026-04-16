from __future__ import annotations
from typing import Optional, List, Dict, Any
"""
Service: TransactionService
Orchestrate toàn bộ luồng submit giao dịch:
  1. Kiểm tra idempotency
  2. Load customer, merchant từ DB
  3. Tính velocity features và cập nhật stats
  4. Gọi FraudScoringService để lấy fraud score
  5. Quyết định và lưu kết quả
  6. Tạo ReviewCase nếu MANUAL_REVIEW
  7. Ghi audit log và state history
"""

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import IdempotencyConflictError, NotFoundError
from app.core.logging import get_logger
from app.models.scoring import AuditLog, RiskScoringResult
from app.models.transaction import Transaction, TxnIdempotency, TxnStateHistory
from app.models.case import ReviewCase, ReviewCaseAction
from app.repositories.transaction_repo import TransactionRepository
from app.repositories.user_repo import UserRepository
from app.repositories.velocity_repo import CustomerRepository, MerchantRepository, VelocityRepository
from app.schemas.transaction import TransactionSubmitRequest, TransactionSubmitResponse
from app.services.fraud_scoring_service import FraudScoringInput, FraudScoringService
from app.utils.card import hash_card_number, mask_card_number

logger = get_logger(__name__)


class TransactionService:
    """Orchestrator cho submit giao dịch."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._txn_repo = TransactionRepository(db)
        self._customer_repo = CustomerRepository(db)
        self._merchant_repo = MerchantRepository(db)
        self._velocity_repo = VelocityRepository(db)
        self._scoring_svc = FraudScoringService.get_instance()

    # ============================================================
    # Public API
    # ============================================================

    def submit(
        self,
        request: TransactionSubmitRequest,
        submitted_by_user_id: str,
    ) -> TransactionSubmitResponse:
        """
        Submit giao dịch mới và chấm điểm fraud ngay lập tức.

        Returns:
            TransactionSubmitResponse với status và fraud score

        Raises:
            IdempotencyConflictError: nếu cùng idempotency_key đã xử lý
            NotFoundError: nếu customer hoặc merchant không tồn tại
        """
        # ---- Bước 1: Idempotency check ----
        if request.idempotency_key:
            cached = self._check_idempotency(request.idempotency_key)
            if cached:
                return cached

        # ---- Bước 2: Load entities ----
        customer = self._customer_repo.get_by_id(request.customer_id)
        if customer is None:
            raise NotFoundError("Customer")

        merchant = self._merchant_repo.get_by_id(request.merchant_id)
        if merchant is None:
            raise NotFoundError("Merchant")

        # ---- Bước 3: Hash card number ----
        card_hash = hash_card_number(request.card_number)
        card_masked = mask_card_number(request.card_number)

        # ---- Bước 4: Cập nhật velocity stats (trước khi score) ----
        txn_date_str = request.txn_time.strftime("%Y-%m-%d")
        velocity = self._velocity_repo.upsert(card_hash, float(request.amount), txn_date_str)

        # ---- Bước 5: Build scoring input ----
        scoring_input = FraudScoringInput(
            amount=float(request.amount),
            txn_time=request.txn_time,
            category=merchant.merchant_category or "misc_net",
            merchant_name=merchant.merchant_name,
            gender=customer.gender or "M",
            job=customer.job or "unknown",
            city=customer.city or "unknown",
            state=customer.state or "unknown",
            city_population=customer.city_population or 50000,
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

        # ---- Bước 6: Score ----
        scoring_result = self._scoring_svc.score(scoring_input)
        logger.info(
            "fraud_scored",
            customer_id=request.customer_id,
            fraud_score=scoring_result.fraud_score,
            decision=scoring_result.decision,
        )

        # ---- Bước 7: Lưu Transaction ----
        txn = Transaction(
            txn_id=str(uuid.uuid4()),
            customer_id=request.customer_id,
            merchant_id=request.merchant_id,
            channel_id=request.channel_id,
            submitted_by=submitted_by_user_id,
            card_number_masked=card_masked,
            card_number_hash=card_hash,
            amount=request.amount,
            currency_code=request.currency_code,
            txn_time=request.txn_time,
            status=scoring_result.decision,
            fraud_score=scoring_result.fraud_score,
            reason_code="HIGH_FRAUD_SCORE" if scoring_result.decision == "REJECTED" else None,
            source_ip=request.source_ip,
        )
        self._txn_repo.create(txn)

        # ---- Bước 8: Lưu scoring result ----
        risk_record = RiskScoringResult(
            score_id=str(uuid.uuid4()),
            txn_id=txn.txn_id,
            model_version=scoring_result.model_version,
            fraud_score=scoring_result.fraud_score,
            decision_suggested=scoring_result.decision,
            reject_threshold=scoring_result.reject_threshold,
            review_threshold=scoring_result.review_threshold,
            feature_snapshot_json=json.dumps(scoring_result.feature_snapshot),
            reason_json=json.dumps({"top_features": scoring_result.top_risk_factors}),
        )
        self._db.add(risk_record)

        # ---- Bước 9: Tạo ReviewCase nếu MANUAL_REVIEW ----
        case_id = None
        if scoring_result.decision == "MANUAL_REVIEW":
            case = ReviewCase(
                case_id=str(uuid.uuid4()),
                txn_id=txn.txn_id,
                case_status="OPEN",
            )
            self._db.add(case)
            self._db.flush()
            case_id = case.case_id
            logger.info("review_case_created", case_id=case_id, txn_id=txn.txn_id)

        # ---- Bước 10: Ghi state history ----
        history = TxnStateHistory(
            state_hist_id=str(uuid.uuid4()),
            txn_id=txn.txn_id,
            old_status=None,
            new_status=scoring_result.decision,
            changed_by_user_id=submitted_by_user_id,
            change_reason=f"AI score: {scoring_result.fraud_score:.4f}",
        )
        self._txn_repo.append_state_history(history)

        # ---- Bước 11: Ghi audit log ----
        audit = AuditLog(
            log_id=str(uuid.uuid4()),
            event_type="TRANSACTION_SUBMITTED",
            entity_type="Transaction",
            entity_id=txn.txn_id,
            actor_user_id=submitted_by_user_id,
            detail_json=json.dumps({
                "amount": float(request.amount),
                "fraud_score": scoring_result.fraud_score,
                "decision": scoring_result.decision,
            }),
        )
        self._db.add(audit)

        # ---- Commit ----
        self._db.commit()

        # ---- Cập nhật idempotency response ----
        response = TransactionSubmitResponse(
            txn_id=txn.txn_id,
            status=scoring_result.decision,
            fraud_score=scoring_result.fraud_score,
            decision=scoring_result.decision,
            message=self._decision_message(scoring_result.decision),
            case_id=case_id,
        )

        if request.idempotency_key:
            self._txn_repo.update_idempotency(
                key=request.idempotency_key,
                status="SUCCESS",
                txn_id=txn.txn_id,
                response_json=json.dumps(response.model_dump()),
            )
            self._db.commit()

        return response

    def get_transaction(self, txn_id: str) -> Transaction:
        """Lấy chi tiết 1 giao dịch theo ID."""
        txn = self._txn_repo.get_by_id(txn_id)
        if txn is None:
            raise NotFoundError("Transaction")
        return txn

    def list_transactions(self, **kwargs) -> tuple[list[Transaction], int]:
        """Danh sách giao dịch với filter và pagination."""
        return self._txn_repo.list_transactions(**kwargs)

    # ============================================================
    # Private helpers
    # ============================================================

    def _check_idempotency(self, key: str) -> Optional[TransactionSubmitResponse]:
        """
        Kiểm tra idempotency key.
        - IN_PROGRESS: raise conflict (đang xử lý)
        - SUCCESS: trả lại response cũ
        - Không tồn tại: tạo record mới, return None để tiếp tục
        """
        record = self._txn_repo.get_idempotency(key)

        if record is None:
            # Chưa có → tạo record báo đang xử lý
            new_record = TxnIdempotency(
                idempotency_key=key,
                status="IN_PROGRESS",
            )
            self._txn_repo.create_idempotency(new_record)
            self._db.commit()
            return None

        if record.status == "IN_PROGRESS":
            raise IdempotencyConflictError()

        if record.status == "SUCCESS" and record.response_snapshot_json:
            # Trả lại kết quả đã xử lý trước
            return TransactionSubmitResponse(**json.loads(record.response_snapshot_json))

        return None

    @staticmethod
    def _decision_message(decision: str) -> str:
        messages = {
            "APPROVED": "Giao dịch đã được chấp thuận.",
            "REJECTED": "Giao dịch bị từ chối do nghi ngờ gian lận.",
            "MANUAL_REVIEW": "Giao dịch đang chờ xem xét thủ công.",
        }
        return messages.get(decision, "Đã xử lý.")
