from __future__ import annotations
"""
Repository: ModelConfigRepository (ERD v2)
SuppressionRepository dropped.
"""

from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.analyst import ModelConfig


class ModelConfigRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_all(self) -> list[ModelConfig]:
        return self._db.query(ModelConfig).order_by(ModelConfig.model_name, ModelConfig.param_name).all()

    def get(self, model_name: str, param_name: str) -> Optional[ModelConfig]:
        model_name_norm = model_name.lower()
        param_name_norm = param_name.lower()
        return self._db.query(ModelConfig).filter(
            func.lower(ModelConfig.model_name) == model_name_norm,
            func.lower(ModelConfig.param_name) == param_name_norm,
        ).first()

    def get_by_model(self, model_name: str) -> list[ModelConfig]:
        model_name_norm = model_name.lower()
        return self._db.query(ModelConfig).filter(
            func.lower(ModelConfig.model_name) == model_name_norm
        ).order_by(ModelConfig.param_name).all()

    def create(
        self,
        model_name: str,
        param_name: str,
        param_value: float,
        description: Optional[str] = None,
        updated_by: Optional[str] = None,
    ) -> ModelConfig:
        cfg = ModelConfig(
            model_name=model_name.lower(),
            param_name=param_name.lower(),
            param_value=param_value,
            description=description,
            updated_by=updated_by,
            version=1,
        )
        self._db.add(cfg)
        return cfg

    def update(self, model_name: str, param_name: str, param_value: float, updated_by: str) -> Optional[ModelConfig]:
        cfg = self.get(model_name, param_name)
        if cfg is None:
            return None
        cfg.param_value = param_value
        cfg.updated_by = updated_by
        cfg.version += 1
        return cfg
