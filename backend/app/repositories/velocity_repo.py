from __future__ import annotations
"""
Repository: Customer, Merchant, CardVelocityStats
Data access layer cho customer/merchant lookup và velocity cache.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.card_velocity import CardVelocityStats
from app.models.customer import Customer
from app.models.merchant import Merchant


class CustomerRepository:
    """Thao tác DB cho Customer."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, customer_id: str) -> Optional[Customer]:
        return self._db.query(Customer).filter(Customer.customer_id == customer_id).first()


class MerchantRepository:
    """Thao tác DB cho Merchant."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, merchant_id: str) -> Optional[Merchant]:
        return self._db.query(Merchant).filter(Merchant.merchant_id == merchant_id).first()


class VelocityRepository:
    """
    Thao tác DB cho CardVelocityStats.
    Dùng Welford's online algorithm để cập nhật mean/std mà không cần lưu toàn bộ lịch sử.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_card_hash(self, card_hash: str) -> Optional[CardVelocityStats]:
        """Lấy velocity stats hiện tại của một thẻ."""
        return self._db.query(CardVelocityStats).filter(
            CardVelocityStats.card_hash == card_hash
        ).first()

    def upsert(self, card_hash: str, new_amount: float, txn_date_str: str) -> CardVelocityStats:
        """
        Cập nhật velocity stats sau mỗi giao dịch mới.
        Dùng Welford's online algorithm để tính mean và variance ngay tại đây.

        Args:
            card_hash: SHA256 của số thẻ
            new_amount: Số tiền của giao dịch mới (USD)
            txn_date_str: Ngày giao dịch "YYYY-MM-DD" — dùng để đếm distinct days
        """
        stats = self.get_by_card_hash(card_hash)

        if stats is None:
            # Lần đầu gặp thẻ này — khởi tạo
            stats = CardVelocityStats(
                card_hash=card_hash,
                total_txn=1,
                avg_amt=new_amount,
                std_amt=0.0,
                m2_amt=0.0,
                distinct_days=1,
                last_txn_date=txn_date_str,
                avg_daily_txn=1.0,
            )
            self._db.add(stats)
        else:
            # Welford's online update
            old_count = stats.total_txn
            new_count = old_count + 1
            delta = new_amount - float(stats.avg_amt)
            new_avg = float(stats.avg_amt) + delta / new_count
            delta2 = new_amount - new_avg
            new_m2 = float(stats.m2_amt) + delta * delta2
            new_std = (new_m2 / new_count) ** 0.5 if new_count > 1 else 0.0

            # Đếm số ngày giao dịch duy nhất
            if stats.last_txn_date != txn_date_str:
                new_distinct_days = stats.distinct_days + 1
            else:
                new_distinct_days = stats.distinct_days

            stats.total_txn = new_count
            stats.avg_amt = new_avg
            stats.std_amt = new_std
            stats.m2_amt = new_m2
            stats.distinct_days = new_distinct_days
            stats.last_txn_date = txn_date_str
            stats.avg_daily_txn = new_count / new_distinct_days

        self._db.flush()
        return stats
