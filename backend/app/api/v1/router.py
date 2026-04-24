"""
API v1 Router — tổng hợp tất cả route modules.
"""

from fastapi import APIRouter

from app.api.v1.routes import (
    analyst,
    audit_logs,
    auth,
    cases,
    dashboard,
    health,
    loan,
    reports,
    transactions,
    users,
)

router = APIRouter()

router.include_router(analyst.router)
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(transactions.router)
router.include_router(cases.router)
router.include_router(loan.router)
router.include_router(audit_logs.router)
router.include_router(dashboard.router)
router.include_router(reports.router)
router.include_router(health.router)
