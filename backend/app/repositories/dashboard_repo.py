from __future__ import annotations
"""
Repository: DashboardRepository
Aggregation queries cho dashboard và report export.
Tất cả queries là READ-ONLY — không có write operations.

Hỗ trợ Oracle (production) và SQLite (dev fallback).
Date truncation được xử lý riêng theo dialect.
"""

from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.base import engine
from app.models.case import ReviewCase
from app.models.loan import Loan
from app.models.transaction import Transaction


def _day_trunc_expr(col: Any) -> Any:
    """
    Trả về SQLAlchemy expression cắt datetime xuống ngày (bỏ phần giờ/phút/giây).
    - Oracle: TRUNC(col)              — tích hợp sẵn, chính xác
    - SQLite: DATE(col)               — trả chuỗi 'YYYY-MM-DD'
    - PostgreSQL: DATE_TRUNC('day')   — trả timestamp lúc midnight
    """
    dialect = engine.dialect.name
    if dialect == "oracle":
        return func.trunc(col)
    # SQLite và PostgreSQL đều dùng được DATE()
    return func.date(col)


class DashboardRepository:
    """Aggregation queries — chỉ đọc."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ============================================================
    # Transaction aggregations
    # ============================================================

    def get_txn_counts_by_status(self) -> dict[str, int]:
        """
        Đếm transactions GROUP BY status.
        Returns: {"APPROVED": 120, "REJECTED": 30, ...}
        """
        rows = (
            self._db.query(
                Transaction.status,
                func.count(Transaction.txn_id).label("cnt"),
            )
            .group_by(Transaction.status)
            .all()
        )
        return {status: cnt for status, cnt in rows}

    def get_txn_count_since(self, since: datetime) -> int:
        """Đếm transactions được tạo từ thời điểm `since` trở đi (dùng created_at)."""
        result = (
            self._db.query(func.count(Transaction.txn_id))
            .filter(Transaction.created_at >= since)
            .scalar()
        )
        return result or 0

    def get_avg_fraud_score(self) -> Optional[float]:
        """Điểm fraud trung bình trên toàn bộ giao dịch có fraud_score."""
        result = (
            self._db.query(func.avg(Transaction.fraud_score))
            .filter(Transaction.fraud_score.isnot(None))
            .scalar()
        )
        return float(result) if result is not None else None

    # ============================================================
    # Case aggregations
    # ============================================================

    def get_case_counts_by_status(self) -> dict[str, int]:
        """Đếm review cases GROUP BY case_status."""
        rows = (
            self._db.query(
                ReviewCase.case_status,
                func.count(ReviewCase.case_id).label("cnt"),
            )
            .group_by(ReviewCase.case_status)
            .all()
        )
        return {status: cnt for status, cnt in rows}

    def get_cases_decided_today(self, today_start: datetime) -> int:
        """Số cases đã được quyết định (decided_at) trong ngày hôm nay."""
        result = (
            self._db.query(func.count(ReviewCase.case_id))
            .filter(
                ReviewCase.decided_at >= today_start,
                ReviewCase.decided_at.isnot(None),
            )
            .scalar()
        )
        return result or 0

    # ============================================================
    # Loan aggregations
    # ============================================================

    def get_loan_counts_by_status(self) -> dict[str, int]:
        """Đếm loans GROUP BY status."""
        try:
            rows = (
                self._db.query(
                    Loan.status,
                    func.count(Loan.loan_id).label("cnt"),
                )
                .group_by(Loan.status)
                .all()
            )
            return {status: cnt for status, cnt in rows}
        except Exception:
            # Loans table may not exist yet in fresh install
            return {}

    # ============================================================
    # Fraud trend queries
    # ============================================================

    def get_fraud_trend_daily(
        self,
        cutoff: datetime,
        max_points: int = 90,
    ) -> list[dict]:
        """
        Đếm transactions GROUP BY ngày và status, từ ngày `cutoff` đến nay.
        Trả về list of dict: {day: date, status: str, cnt: int}
        Service layer sẽ pivot thành FraudTrendPoint per day.

        max_points: giới hạn số ngày tối đa — ngăn query quá lớn.
        """
        day_expr = _day_trunc_expr(Transaction.txn_time)

        rows = (
            self._db.query(
                day_expr.label("day"),
                Transaction.status,
                func.count(Transaction.txn_id).label("cnt"),
            )
            .filter(Transaction.txn_time >= cutoff)
            .group_by(day_expr, Transaction.status)
            .order_by(day_expr)
            .limit(max_points * 4)   # 4 statuses per day max
            .all()
        )

        result = []
        for day_val, status, cnt in rows:
            result.append({
                "day": day_val,
                "status": status,
                "cnt": cnt,
            })
        return result

    # ============================================================
    # Report export queries
    # ============================================================

    def get_transactions_for_export(
        self,
        status: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        max_rows: int = 5000,
    ) -> list[Transaction]:
        """
        Fetch transactions cho export — có giới hạn max_rows.
        Eager-load không cần thiết vì chỉ export field từ transactions_live.
        Sắp xếp theo txn_time giảm dần (mới nhất trước).
        """
        query = self._db.query(Transaction)

        if status:
            query = query.filter(Transaction.status == status)
        if from_date:
            query = query.filter(Transaction.txn_time >= from_date)
        if to_date:
            query = query.filter(Transaction.txn_time <= to_date)

        return (
            query.order_by(Transaction.txn_time.desc())
            .limit(max_rows)
            .all()
        )

    def get_fraud_summary_for_export(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> list[dict]:
        """
        Fraud summary báo cáo: GROUP BY ngày và status.
        Cùng logic với get_fraud_trend_daily nhưng không giới hạn max_points.
        Dùng cho export báo cáo fraud toàn bộ khoảng thời gian.
        """
        day_expr = _day_trunc_expr(Transaction.txn_time)
        query = (
            self._db.query(
                day_expr.label("day"),
                Transaction.status,
                func.count(Transaction.txn_id).label("cnt"),
                func.avg(Transaction.fraud_score).label("avg_score"),
            )
            .group_by(day_expr, Transaction.status)
            .order_by(day_expr)
        )

        if from_date:
            query = query.filter(Transaction.txn_time >= from_date)
        if to_date:
            query = query.filter(Transaction.txn_time <= to_date)

        rows = query.limit(10000).all()
        return [
            {"day": day_val, "status": status, "cnt": cnt, "avg_score": avg_score}
            for day_val, status, cnt, avg_score in rows
        ]
