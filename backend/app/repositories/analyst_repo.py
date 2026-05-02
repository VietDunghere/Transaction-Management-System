from __future__ import annotations
"""
Repository: ModelConfigRepository (ERD v2)
SuppressionRepository dropped.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.analyst import ModelConfig


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
