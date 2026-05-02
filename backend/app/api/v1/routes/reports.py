from __future__ import annotations
"""
Router: Reports (Export)
GET /reports/transactions   — export giao dịch (CSV hoặc JSON)
GET /reports/fraud          — export báo cáo fraud summary (CSV hoặc JSON)

Cả hai endpoints đều hỗ trợ ?format=csv (attachment download) hoặc ?format=json.
Giới hạn: max 5000 rows mỗi lần export để bảo vệ DB.
Chỉ MANAGER và ADMIN mới truy cập được.
"""

import csv
import io
import json
from collections import defaultdict
from datetime import date, datetime, timezone
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response

from app.api.v1.deps import require_roles
from app.db.deps import DbSession
from app.repositories.dashboard_repo import DashboardRepository
from app.schemas.auth import TokenPayload
from app.services.dashboard_service import _to_date, _safe_rate

router = APIRouter(prefix="/reports", tags=["Reports"])

_EXPORT_LIMIT = 5000   # Hard cap để tránh export quá lớn làm chết DB


# ============================================================
# Helpers
# ============================================================

def _csv_response(rows: list[dict], filename: str) -> Response:
    """
    Tạo Response trả về CSV dạng bytes (UTF-8 với BOM).
    Dùng Response thay vì StreamingResponse vì toàn bộ content đã có trong RAM
    (giới hạn 5000 rows). BOM (utf-8-sig) giúp Excel/Numbers nhận diện encoding đúng.
    """
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    content_bytes = output.getvalue().encode("utf-8-sig")

    return Response(
        content=content_bytes,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _json_response(rows: list[dict]) -> JSONResponse:
    """Trả JSON array — không dùng response_model để linh hoạt schema."""
    return JSONResponse(content=rows)


def _fmt_float(val) -> Optional[float]:
    """Chuyển Decimal/None sang float an toàn cho JSON serialization."""
    if val is None:
        return None
    try:
        return round(float(val), 4)
    except (TypeError, ValueError):
        return None


def _fmt_dt(val) -> Optional[str]:
    """Chuyển datetime/date sang ISO string."""
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.isoformat()
    if isinstance(val, date):
        return val.isoformat()
    return str(val)


# ============================================================
# Endpoints
# ============================================================

@router.get(
    "/transactions",
    response_class=Response,
    responses={
        200: {
            "description": "CSV download hoặc JSON array giao dịch",
            "content": {
                "text/csv": {},
                "application/json": {},
            },
        }
    },
    summary="Export danh sách giao dịch",
    description=(
        f"Export tối đa {_EXPORT_LIMIT} giao dịch dưới dạng CSV hoặc JSON. "
        "Hỗ trợ filter theo status và khoảng thời gian (txn_time). "
        "CSV sẽ tự động download; JSON trả về array thuần. "
        "Chỉ MANAGER và ADMIN mới truy cập được."
    ),
)
def export_transactions(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("MANAGER", "ADMIN")),
    format: Literal["csv", "json"] = Query(
        default="json",
        description="Định dạng output: 'csv' (download) hoặc 'json'",
    ),
    status: Optional[str] = Query(
        None, description="Lọc theo status: APPROVED | REJECTED | MANUAL_REVIEW | PENDING"
    ),
    from_date: Optional[datetime] = Query(
        None, description="Từ ngày txn_time (ISO 8601)"
    ),
    to_date: Optional[datetime] = Query(
        None, description="Đến ngày txn_time (ISO 8601)"
    ),
) -> Response:
    repo = DashboardRepository(db)
    transactions = repo.get_transactions_for_export(
        status=status,
        from_date=from_date,
        to_date=to_date,
        max_rows=_EXPORT_LIMIT,
    )

    rows = [
        {
            "txn_id":             t.txn_id,
            "customer_id":        t.customer_id,
            "merchant_id":        t.merchant_id,
            "channel_id":         t.channel_id,
            "card_number_masked": t.card_number_masked,
            "amount":             _fmt_float(t.amount),
            "txn_time":           _fmt_dt(t.txn_time),
            "status":             t.status,
            "fraud_score":        _fmt_float(t.fraud_score),
            "created_at":         _fmt_dt(t.created_at),
        }
        for t in transactions
    ]

    today_str = datetime.now(timezone.utc).date().isoformat()
    if format == "csv":
        return _csv_response(rows, filename=f"transactions_{today_str}.csv")
    return _json_response(rows)


@router.get(
    "/fraud",
    response_class=Response,
    responses={
        200: {
            "description": "CSV download hoặc JSON array báo cáo fraud summary theo ngày",
            "content": {
                "text/csv": {},
                "application/json": {},
            },
        }
    },
    summary="Export báo cáo fraud summary",
    description=(
        "Export báo cáo fraud tổng hợp theo ngày: "
        "mỗi row là 1 ngày với số lượng giao dịch theo status và tỷ lệ fraud. "
        "Hỗ trợ filter theo khoảng thời gian. "
        "Chỉ MANAGER và ADMIN mới truy cập được."
    ),
)
def export_fraud_report(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("MANAGER", "ADMIN")),
    format: Literal["csv", "json"] = Query(
        default="json",
        description="Định dạng output: 'csv' (download) hoặc 'json'",
    ),
    from_date: Optional[datetime] = Query(
        None, description="Từ ngày (ISO 8601)"
    ),
    to_date: Optional[datetime] = Query(
        None, description="Đến ngày (ISO 8601)"
    ),
) -> Response:
    repo = DashboardRepository(db)
    raw_rows = repo.get_fraud_summary_for_export(
        from_date=from_date,
        to_date=to_date,
    )

    # ---- Pivot: (day, status, cnt, avg_score) → 1 row per day ----
    day_data: dict[date, dict] = defaultdict(lambda: {
        "approved": 0, "rejected": 0, "manual_review": 0,
        "pending": 0, "avg_score_sum": 0.0, "avg_score_count": 0,
    })

    for row in raw_rows:
        d = _to_date(row["day"])
        status = row["status"]
        cnt = row["cnt"]
        avg_s = _fmt_float(row["avg_score"]) or 0.0

        day_data[d][status.lower()] = day_data[d].get(status.lower(), 0) + cnt
        if avg_s:
            day_data[d]["avg_score_sum"] += avg_s * cnt
            day_data[d]["avg_score_count"] += cnt

    # ---- Flatten to list of dicts ----
    output_rows = []
    for d in sorted(day_data.keys()):
        counts = day_data[d]
        total = counts["approved"] + counts["rejected"] + counts["manual_review"] + counts["pending"]
        avg_score_count = counts["avg_score_count"]
        avg_score = (
            round(counts["avg_score_sum"] / avg_score_count, 4)
            if avg_score_count > 0 else None
        )
        output_rows.append({
            "date":              d.isoformat(),
            "total_txn":         total,
            "approved":          counts["approved"],
            "rejected":          counts["rejected"],
            "manual_review":     counts["manual_review"],
            "pending":           counts["pending"],
            "fraud_rate":        _safe_rate(counts["rejected"], total),
            "avg_fraud_score":   avg_score,
        })

    today_str = datetime.now(timezone.utc).date().isoformat()
    if format == "csv":
        return _csv_response(output_rows, filename=f"fraud_report_{today_str}.csv")
    return _json_response(output_rows)
