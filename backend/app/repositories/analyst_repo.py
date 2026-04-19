from __future__ import annotations
"""
Repository: ModelConfigRepository + SuppressionRepository
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.analyst import ModelConfig, SuppressionRule


class ModelConfigRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_all(self) -> list[ModelConfig]:
        return self._db.query(ModelConfig).order_by(ModelConfig.model_name, ModelConfig.param_name).all()

    def get(self, model_name: str, param_name: str) -> Optional[ModelConfig]:
        return self._db.query(ModelConfig).filter(
            ModelConfig.model_name == model_name,
            ModelConfig.param_name == param_name,
        ).first()

    def get_by_model(self, model_name: str) -> list[ModelConfig]:
        return self._db.query(ModelConfig).filter(ModelConfig.model_name == model_name).all()

    def update(self, model_name: str, param_name: str, param_value: float, updated_by: str) -> Optional[ModelConfig]:
        cfg = self.get(model_name, param_name)
        if cfg is None:
            return None
        cfg.param_value = param_value
        cfg.updated_by = updated_by
        cfg.version += 1
        return cfg


class SuppressionRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_active(self) -> list[SuppressionRule]:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return self._db.query(SuppressionRule).filter(
            SuppressionRule.is_active == True,  # noqa: E712
            (SuppressionRule.expires_at == None) | (SuppressionRule.expires_at > now),  # noqa: E711
        ).all()

    def list_all(self, include_inactive: bool = False) -> list[SuppressionRule]:
        q = self._db.query(SuppressionRule)
        if not include_inactive:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            q = q.filter(
                SuppressionRule.is_active == True,  # noqa: E712
                (SuppressionRule.expires_at == None) | (SuppressionRule.expires_at > now),  # noqa: E711
            )
        return q.order_by(SuppressionRule.created_at.desc()).all()

    def get(self, rule_id: str) -> Optional[SuppressionRule]:
        return self._db.query(SuppressionRule).filter(SuppressionRule.rule_id == rule_id).first()

    def create(self, rule: SuppressionRule) -> SuppressionRule:
        self._db.add(rule)
        return rule

    def deactivate(self, rule_id: str) -> Optional[SuppressionRule]:
        rule = self.get(rule_id)
        if rule:
            rule.is_active = False
        return rule

    def is_suppressed(self, merchant_id: str | None, customer_id: str | None, card_hash: str | None) -> bool:
        """Kiểm tra nhanh xem giao dịch có bị suppress không."""
        active = self.list_active()
        for rule in active:
            if rule.rule_type == "MERCHANT" and rule.entity_id == merchant_id:
                return True
            if rule.rule_type == "CUSTOMER" and rule.entity_id == customer_id:
                return True
            if rule.rule_type == "CARD_HASH" and rule.entity_id == card_hash:
                return True
        return False
