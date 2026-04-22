from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context

# ── Thêm backend/ vào sys.path để import app.* ────────────────
sys.path.insert(0, str(Path(__file__).parents[1]))

from app.core.config import get_settings
from app.db.base import Base  # noqa: F401

# Import tất cả models để Base.metadata biết đủ bảng
from app.models import (  # noqa: F401
    analyst,
    audit_log,
    card_velocity,
    case,
    customer,
    etl_log,
    loan,
    merchant,
    reconciliation,
    scoring,
    transaction,
    user,
)

# ── Alembic config ─────────────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override DATABASE_URL từ .env (bỏ qua placeholder trong alembic.ini)
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata


# ── Offline mode (tạo SQL script, không cần DB thật) ──────────
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Oracle: không dùng schema mặc định, dùng owner hiện tại
        include_schemas=False,
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online mode (kết nối DB thật) ─────────────────────────────
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=False,
            # Với Oracle: compare_type=True để detect thay đổi kiểu cột
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
