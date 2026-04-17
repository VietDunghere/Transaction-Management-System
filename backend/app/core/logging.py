from __future__ import annotations
"""
Structured logging với structlog.
Mọi log đều ở dạng JSON trong production để dễ index vào ELK/CloudWatch.
"""

import logging
import sys

import structlog

from app.core.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """
    Khởi tạo structlog.
    - Development: human-friendly console output có màu
    - Production: JSON output dễ parse bằng log aggregator
    """
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.is_production:
        # JSON format cho production
        renderer = structlog.processors.JSONRenderer()
    else:
        # Đẹp hơn cho dev
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)


def get_logger(name: str = __name__) -> structlog.stdlib.BoundLogger:
    """Lấy logger đã được cấu hình structlog."""
    return structlog.get_logger(name)
