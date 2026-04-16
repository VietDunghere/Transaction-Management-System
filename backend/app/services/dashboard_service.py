from __future__ import annotations
"""
Service: DashboardService
Tổng hợp dữ liệu analytics từ nhiều bảng.
Tất cả methods là read-only — không có side effects.
"""

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.repositories.dashboard_repo import DashboardRepository
from app.schemas.dashboard import (
    CaseStats,
    DashboardSummary,
    FraudStats,
    FraudTrendPoint,
    FraudTrendResponse,
    LoanStats,
    TransactionStats,
)


def _to_date(val: Any) -> date:
    """
    Chuẩn hoá giá trị ngày trả về từ DB về Python date.
    - Oracle TRUNC() → datetime → .date()
    - SQLite DATE() → str 'YYYY-MM-DD' → date.fromisoformat()
    - date  → trả luôn
    """
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    if isinstance(val, str):
        return date.fromisoformat(val[:10])
    raise TypeError(f"Cannot convert {type(val)} to date: {val!r}")


def _safe_rate(numerator: int, denominator: int) -> float:
    """Tính tỷ lệ an toàn — trả 0.0 nếu mẫu = 0."""
    return round(numerator / denominator, 4) if denominator > 0 else 0.0


def _utc_today_start() -> datetime:
    """Thời điểm đầu ngày hôm nay theo UTC (midnight)."""
    today = datetime.now(timezone.utc).date()
    return datetime(today.year, today.month, today.day, tzinfo=timezone.utc)


def _utc_week_start() -> datetime:
    """Thứ Hai đầu tuần này theo UTC (ISO week — weekday() = 0 là thứ Hai)."""
    today = datetime.now(timezone.utc).date()
    monday = today - timedelta(days=today.weekday())
    return datetime(monday.year, monday.month, monday.day, tzinfo=timezone.utc)


class DashboardService:
    """Analytics read-only service."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = DashboardRepository(db)

    def get_summary(self) -> DashboardSummary:
        """
        Lấy toàn bộ dashboard summary trong 1 lần gọi.
        Thực hiện ~6 DB queries nhỏ — tất cả đều dùng index.
        """
        today_start = _utc_today_start()
        week_start = _utc_week_start()

        # ---- Transactions ----
        txn_counts = self._repo.get_txn_counts_by_status()
        total_txn = sum(txn_counts.values())
        approved = txn_counts.get("APPROVED", 0)
        rejected = txn_counts.get("REJECTED", 0)
        manual_review = txn_counts.get("MANUAL_REVIEW", 0)
        pending = txn_counts.get("PENDING", 0)

        txn_today = self._repo.get_txn_count_since(today_start)
        txn_week = self._repo.get_txn_count_since(week_start)

        # ---- Fraud stats ----
        avg_score = self._repo.get_avg_fraud_score()

        # ---- Cases ----
        case_counts = self._repo.get_case_counts_by_status()
        decided_today = self._repo.get_cases_decided_today(today_start)

        # ---- Loans ----
        loan_counts = self._repo.get_loan_counts_by_status()

        return DashboardSummary(
            transactions=TransactionStats(
                total=total_txn,
                approved=approved,
                rejected=rejected,
                manual_review=manual_review,
                pending=pending,
                today=txn_today,
                this_week=txn_week,
            ),
            fraud=FraudStats(
                avg_fraud_score=round(avg_score, 4) if avg_score is not None else None,
                rejection_rate=_safe_rate(rejected, total_txn),
                manual_review_rate=_safe_rate(manual_review, total_txn),
            ),
            cases=CaseStats(
                total_open=case_counts.get("OPEN", 0),
                total_assigned=case_counts.get("ASSIGNED", 0),
                decided_today=decided_today,
            ),
            loans=LoanStats(
                total_pending=loan_counts.get("PENDING", 0),
                total_approved=loan_counts.get("APPROVED", 0),
                total_rejected=loan_counts.get("REJECTED", 0),
            ),
            as_of=datetime.now(timezone.utc),
        )

    def get_fraud_trend(self, lookback_days: int = 30) -> FraudTrendResponse:
        """
        Trả về biểu đồ trend giao dịch/fraud theo ngày trong N ngày gần nhất.
        Kết quả có mặt cả những ngày không có giao dịch nào (zero-fill).

        lookback_days: 1–90 ngày (caller đã validate).
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        raw_rows = self._repo.get_fraud_trend_daily(cutoff, max_points=lookback_days)

        # ---- Pivot: (day, status, cnt) → per-day totals ----
        # defaultdict đảm bảo các ngày không có giao dịch vẫn được đại diện
        # (zero-fill sẽ xử lý sau)
        day_data: dict[date, dict[str, int]] = defaultdict(
            lambda: {"approved": 0, "rejected": 0, "manual_review": 0, "pending": 0}
        )

        for row in raw_rows:
            d = _to_date(row["day"])
            status = row["status"]
            cnt = row["cnt"]
            if status == "APPROVED":
                day_data[d]["approved"] += cnt
            elif status == "REJECTED":
                day_data[d]["rejected"] += cnt
            elif status == "MANUAL_REVIEW":
                day_data[d]["manual_review"] += cnt
            elif status == "PENDING":
                day_data[d]["pending"] += cnt

        # ---- Zero-fill: đảm bảo mọi ngày trong window đều có entry ----
        today = datetime.now(timezone.utc).date()
        start_date = (datetime.now(timezone.utc) - timedelta(days=lookback_days - 1)).date()
        all_dates = [start_date + timedelta(days=i) for i in range(lookback_days)]

        trend_points: list[FraudTrendPoint] = []
        for d in all_dates:
            counts = day_data.get(d, {"approved": 0, "rejected": 0, "manual_review": 0, "pending": 0})
            total = sum(counts.values())
            trend_points.append(FraudTrendPoint(
                period_label=d.isoformat(),
                period_start=d,
                total_txn=total,
                approved=counts["approved"],
                rejected=counts["rejected"],
                manual_review=counts["manual_review"],
                fraud_rate=_safe_rate(counts["rejected"], total),
            ))

        return FraudTrendResponse(
            period="daily",
            lookback_days=lookback_days,
            data=trend_points,
            as_of=datetime.now(timezone.utc),
        )
