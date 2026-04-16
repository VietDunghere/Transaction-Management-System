from __future__ import annotations
"""
Repository: EtlRepository, DataLakeRepository
Data access layer cho ETL logs và DataLake snapshots.
"""

from datetime import date
from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from app.models.etl_log import DataLakeSnapshot, EtlLog


class EtlRepository:
    """CRUD cho EtlLog."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, job_id: str) -> Optional[EtlLog]:
        return self._db.query(EtlLog).filter(EtlLog.job_id == job_id).first()

    def list_jobs(
        self,
        job_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[EtlLog], int]:
        query = self._db.query(EtlLog)
        if job_type:
            query = query.filter(EtlLog.job_type == job_type)
        if status:
            query = query.filter(EtlLog.status == status)

        total = query.count()
        items = (
            query.order_by(desc(EtlLog.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def create(self, job: EtlLog) -> EtlLog:
        self._db.add(job)
        self._db.flush()
        return job

    def already_ran_today(self, target_date: date, job_type: str) -> bool:
        """
        Kiểm tra xem đã có job chạy SUCCESS cho target_date và job_type chưa.
        Ngăn chạy lại ETL cho cùng 1 ngày (idempotency guard).
        """
        exists = (
            self._db.query(EtlLog)
            .filter(
                EtlLog.target_date == target_date,
                EtlLog.job_type == job_type,
                EtlLog.status == "SUCCESS",
            )
            .first()
        )
        return exists is not None


class DataLakeRepository:
    """CRUD cho DataLakeSnapshot."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, snapshot_id: str) -> Optional[DataLakeSnapshot]:
        return (
            self._db.query(DataLakeSnapshot)
            .filter(DataLakeSnapshot.snapshot_id == snapshot_id)
            .first()
        )

    def list_snapshots(
        self,
        snapshot_type: Optional[str] = None,
        snapshot_date: Optional[date] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[DataLakeSnapshot], int]:
        query = self._db.query(DataLakeSnapshot)
        if snapshot_type:
            query = query.filter(DataLakeSnapshot.snapshot_type == snapshot_type)
        if snapshot_date:
            query = query.filter(DataLakeSnapshot.snapshot_date == snapshot_date)
        if status:
            query = query.filter(DataLakeSnapshot.status == status)

        total = query.count()
        items = (
            query.order_by(desc(DataLakeSnapshot.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def create(self, snapshot: DataLakeSnapshot) -> DataLakeSnapshot:
        self._db.add(snapshot)
        self._db.flush()
        return snapshot
