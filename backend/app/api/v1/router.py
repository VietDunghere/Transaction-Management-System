"""
API v1 Router — tổng hợp tất cả route modules.
"""

from fastapi import APIRouter

from app.api.v1.routes import auth, cases, health, transactions, users

router = APIRouter()

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(transactions.router)
router.include_router(cases.router)
router.include_router(health.router)
