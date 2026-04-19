from __future__ import annotations
"""
Router: SSE Stream
GET /stream/transactions — real-time feed giao dịch mới (OPERATOR, MANAGER, ADMIN, REVIEWER)
GET /stream/dashboard   — real-time dashboard summary (MANAGER, ADMIN)

Dùng trong demo: Faker gửi POST liên tục → SSE đẩy kết quả về frontend ngay lập tức.
Không cần WebSocket vì chỉ cần server → client (1 chiều).
"""

import asyncio
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.api.v1.deps import require_roles
from app.db.base import SessionLocal
from app.repositories.transaction_repo import TransactionRepository
from app.schemas.auth import TokenPayload
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/stream", tags=["Stream"])


@router.get(
    "/transactions",
    summary="SSE: live transaction feed",
    description=(
        "Server-Sent Events stream — đẩy real-time từng giao dịch mới ngay khi được submit. "
        "Dùng trong demo: Faker POST liên tục, frontend nhận SSE để hiển thị live feed. "
        "Mỗi event là 1 giao dịch dạng JSON. "
        "Heartbeat comment `: ping` được gửi khi không có giao dịch mới."
    ),
)
async def stream_transactions(
    token: TokenPayload = Depends(require_roles("OPERATOR", "MANAGER", "ADMIN", "REVIEWER")),
    interval: float = Query(default=2.0, ge=0.5, le=10.0, description="Poll interval (giây)"),
) -> StreamingResponse:
    async def generator():
        last_checked = datetime.now(timezone.utc)
        yield ": heartbeat\n\n"

        while True:
            await asyncio.sleep(interval)
            db = SessionLocal()
            try:
                repo = TransactionRepository(db)
                items, _ = repo.list_transactions(
                    created_after=last_checked,
                    page=1,
                    page_size=50,
                )
                last_checked = datetime.now(timezone.utc)

                if items:
                    for txn in items:
                        payload = {
                            "txn_id":       txn.txn_id,
                            "customer_id":  txn.customer_id,
                            "merchant_id":  txn.merchant_id,
                            "amount":       float(txn.amount),
                            "currency_code": txn.currency_code,
                            "status":       txn.status,
                            "fraud_score":  float(txn.fraud_score) if txn.fraud_score else None,
                            "txn_time":     txn.txn_time.isoformat() if txn.txn_time else None,
                            "created_at":   txn.created_at.isoformat() if txn.created_at else None,
                        }
                        yield f"data: {json.dumps(payload)}\n\n"
                else:
                    yield ": ping\n\n"

            except Exception:
                yield ": error\n\n"
            finally:
                db.close()

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/dashboard",
    summary="SSE: live dashboard summary",
    description=(
        "Server-Sent Events stream — đẩy dashboard summary cập nhật mỗi N giây. "
        "Bao gồm: transaction counts theo status, fraud rate, case queue, loan stats."
    ),
)
async def stream_dashboard(
    token: TokenPayload = Depends(require_roles("MANAGER", "ADMIN")),
    interval: float = Query(default=5.0, ge=1.0, le=30.0, description="Poll interval (giây)"),
) -> StreamingResponse:
    async def generator():
        yield ": heartbeat\n\n"

        while True:
            await asyncio.sleep(interval)
            db = SessionLocal()
            try:
                svc = DashboardService(db)
                summary = svc.get_summary()
                payload = summary.model_dump(mode="json")
                yield f"data: {json.dumps(payload, default=str)}\n\n"
            except Exception:
                yield ": error\n\n"
            finally:
                db.close()

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
