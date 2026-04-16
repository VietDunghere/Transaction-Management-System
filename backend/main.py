from __future__ import annotations
from typing import Optional, List, Dict, Any
"""
FastAPI Application Entry Point
================================
Khởi động ứng dụng, đăng ký routers, middleware và event handlers.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import router as api_v1_router
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.logging import get_logger, setup_logging
from app.db.base import create_tables
from app.services.fraud_scoring_service import FraudScoringService

settings = get_settings()
logger = get_logger(__name__)


# ============================================================
# Lifecycle hooks
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Chạy khi startup và shutdown.
    - Startup: khởi tạo logging, tạo bảng DB, load ML model
    - Shutdown: cleanup (nếu cần)
    """
    # ---- Startup ----
    setup_logging()
    logger.info("app_starting", env=settings.app_env, debug=settings.debug)

    # Tạo bảng DB (dev mode — production dùng Alembic)
    if settings.app_env != "production":
        create_tables()
        logger.info("db_tables_created")

    # Load fraud detection model ngay khi startup (không delay đến request đầu tiên)
    FraudScoringService.get_instance()

    logger.info("app_started", model_ready=FraudScoringService.get_instance().is_ready)
    yield

    # ---- Shutdown ----
    logger.info("app_shutting_down")


# ============================================================
# App instance
# ============================================================

app = FastAPI(
    title=settings.app_name,
    description=(
        "API cho hệ thống quản lý giao dịch ngân hàng với tích hợp "
        "phát hiện gian lận bằng Random Forest ML model."
    ),
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)


# ============================================================
# Middleware
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Exception handlers — đồng nhất format lỗi toàn API
# ============================================================

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Xử lý tất cả AppException → format JSON chuẩn."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": type(exc).__name__,
            "message": exc.detail,
            "path": str(request.url.path),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all cho lỗi không mong đợi — che giấu chi tiết kỹ thuật."""
    logger.error("unhandled_exception", error=str(exc), path=str(request.url.path))
    return JSONResponse(
        status_code=500,
        content={
            "code": "InternalServerError",
            "message": "Lỗi hệ thống. Vui lòng thử lại sau.",
            "path": str(request.url.path),
        },
    )


# ============================================================
# Routers
# ============================================================

app.include_router(api_v1_router, prefix=settings.api_prefix)
