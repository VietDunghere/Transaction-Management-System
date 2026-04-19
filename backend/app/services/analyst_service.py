from __future__ import annotations
"""
Service: AnalystService
Cung cấp các chức năng dành riêng cho ANALYST:
  1. Threshold management — xem/cập nhật ngưỡng fraud & loan
  2. Model performance — thống kê score distribution, false positive rate
  3. Suppression rules — tạo/vô hiệu hóa whitelist bypass fraud scoring
"""

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.analyst import ModelConfig, SuppressionRule
from app.models.case import ReviewCase
from app.models.loan import Loan
from app.models.scoring import AuditLog
from app.models.transaction import Transaction
from app.repositories.analyst_repo import ModelConfigRepository, SuppressionRepository
from app.schemas.analyst import (
    FraudModelPerformanceResponse,
    FraudScoreDistribution,
    LoanModelPerformanceResponse,
    LoanRiskDistribution,
    SuppressionRuleCreateRequest,
    ThresholdListResponse,
    ThresholdUpdateRequest,
)

logger = get_logger(__name__)


class AnalystService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._config_repo = ModelConfigRepository(db)
        self._suppression_repo = SuppressionRepository(db)

    # ============================================================
    # 1. Threshold management
    # ============================================================

    def get_thresholds(self) -> ThresholdListResponse:
        fraud_cfgs = self._config_repo.get_by_model("fraud")
        loan_cfgs = self._config_repo.get_by_model("loan")
        return ThresholdListResponse(fraud=fraud_cfgs, loan=loan_cfgs)

    def update_thresholds(self, request: ThresholdUpdateRequest, actor_user_id: str) -> ThresholdListResponse:
        for item in request.updates:
            cfg = self._config_repo.update(item.model_name, item.param_name, item.param_value, actor_user_id)
            if cfg is None:
                raise NotFoundError(f"ModelConfig {item.model_name}.{item.param_name}")

        self._db.add(AuditLog(
            log_id=str(uuid.uuid4()),
            event_type="THRESHOLD_UPDATED",
            entity_type="ModelConfig",
            entity_id="batch",
            actor_user_id=actor_user_id,
            detail_json=json.dumps([u.model_dump() for u in request.updates]),
        ))
        self._db.commit()
        logger.info("thresholds_updated", actor=actor_user_id, count=len(request.updates))
        return self.get_thresholds()

    # ============================================================
    # 2. Model performance
    # ============================================================

    def get_fraud_performance(self, days: int = 30) -> FraudModelPerformanceResponse:
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)

        txns = self._db.query(Transaction).filter(Transaction.created_at >= cutoff).all()
        total = len(txns)

        reject_cfg = self._config_repo.get("fraud", "reject_threshold")
        review_cfg = self._config_repo.get("fraud", "review_threshold")
        reject_th = float(reject_cfg.param_value) if reject_cfg else 0.65
        review_th = float(review_cfg.param_value) if review_cfg else 0.35

        approved = sum(1 for t in txns if t.fraud_score is not None and float(t.fraud_score) < review_th)
        rejected = sum(1 for t in txns if t.fraud_score is not None and float(t.fraud_score) >= reject_th)
        review = total - approved - rejected

        # False positive: case MANUAL_REVIEW mà reviewer quyết định APPROVED
        fp_count = self._db.query(ReviewCase).filter(
            ReviewCase.created_at >= cutoff,
            ReviewCase.decision == "APPROVE",
            ReviewCase.case_status == "APPROVED",
        ).count()

        fp_rate = round(fp_count / review, 4) if review > 0 else 0.0

        dist = FraudScoreDistribution(
            approved_count=approved,
            review_count=review,
            rejected_count=rejected,
            total=total,
            approved_rate=round(approved / total, 4) if total > 0 else 0.0,
            review_rate=round(review / total, 4) if total > 0 else 0.0,
            rejected_rate=round(rejected / total, 4) if total > 0 else 0.0,
            false_positive_count=fp_count,
            false_positive_rate=fp_rate,
        )
        return FraudModelPerformanceResponse(
            period_days=days,
            score_distribution=dist,
            current_thresholds={"reject_threshold": reject_th, "review_threshold": review_th},
        )

    def get_loan_performance(self, days: int = 30) -> LoanModelPerformanceResponse:
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)

        loans = self._db.query(Loan).filter(Loan.created_at >= cutoff).all()
        total = len(loans)

        low = sum(1 for l in loans if l.risk_level == "LOW RISK")
        medium = sum(1 for l in loans if l.risk_level == "MEDIUM RISK")
        high = sum(1 for l in loans if l.risk_level == "HIGH RISK")
        approved = sum(1 for l in loans if l.status == "APPROVED")
        rejected = sum(1 for l in loans if l.status == "REJECTED")
        pending = sum(1 for l in loans if l.status == "PENDING")

        high_cfg = self._config_repo.get("loan", "high_risk_threshold")
        medium_cfg = self._config_repo.get("loan", "medium_risk_threshold")

        dist = LoanRiskDistribution(
            low_risk_count=low,
            medium_risk_count=medium,
            high_risk_count=high,
            total=total,
            low_risk_rate=round(low / total, 4) if total > 0 else 0.0,
            medium_risk_rate=round(medium / total, 4) if total > 0 else 0.0,
            high_risk_rate=round(high / total, 4) if total > 0 else 0.0,
            approved_count=approved,
            rejected_count=rejected,
            pending_count=pending,
        )
        return LoanModelPerformanceResponse(
            period_days=days,
            risk_distribution=dist,
            current_thresholds={
                "high_risk_threshold": float(high_cfg.param_value) if high_cfg else 0.50,
                "medium_risk_threshold": float(medium_cfg.param_value) if medium_cfg else 0.20,
            },
        )

    # ============================================================
    # 3. Suppression rules
    # ============================================================

    def list_suppression_rules(self, include_inactive: bool = False) -> list[SuppressionRule]:
        return self._suppression_repo.list_all(include_inactive=include_inactive)

    def create_suppression_rule(self, request: SuppressionRuleCreateRequest, actor_user_id: str) -> SuppressionRule:
        rule = SuppressionRule(
            rule_id=str(uuid.uuid4()),
            rule_type=request.rule_type,
            entity_id=request.entity_id,
            reason=request.reason,
            created_by=actor_user_id,
            expires_at=request.expires_at,
            is_active=True,
        )
        self._suppression_repo.create(rule)
        self._db.add(AuditLog(
            log_id=str(uuid.uuid4()),
            event_type="SUPPRESSION_RULE_CREATED",
            entity_type="SuppressionRule",
            entity_id=rule.rule_id,
            actor_user_id=actor_user_id,
            detail_json=json.dumps({"rule_type": rule.rule_type, "entity_id": rule.entity_id}),
        ))
        self._db.commit()
        self._db.refresh(rule)
        logger.info("suppression_rule_created", rule_id=rule.rule_id, actor=actor_user_id)
        return rule

    def deactivate_suppression_rule(self, rule_id: str, actor_user_id: str) -> SuppressionRule:
        rule = self._suppression_repo.deactivate(rule_id)
        if rule is None:
            raise NotFoundError("SuppressionRule")
        self._db.add(AuditLog(
            log_id=str(uuid.uuid4()),
            event_type="SUPPRESSION_RULE_DEACTIVATED",
            entity_type="SuppressionRule",
            entity_id=rule_id,
            actor_user_id=actor_user_id,
            detail_json=json.dumps({"rule_id": rule_id}),
        ))
        self._db.commit()
        logger.info("suppression_rule_deactivated", rule_id=rule_id, actor=actor_user_id)
        return rule
