from __future__ import annotations
"""
Service: EtlService
ETL pipeline và DataLake ingest.

EtlService.run_etl():
  1. Guard: nếu đã chạy SUCCESS hôm nay → reject (idempotency)
  2. Tạo EtlLog(RUNNING), commit
  3. Query transactions cho target_date
  4. Tổng hợp: counts by status, total amount, avg fraud_score
  5. Ghi DataLakeSnapshot
  6. Update EtlLog(SUCCESS)
  7. Commit và return

EtlService.ingest():
  Nhận batch records từ nguồn ngoài, lưu thẳng vào DataLakeSnapshot.
"""

import json
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import AppException, ConflictError
from app.core.logging import get_logger
from app.models.etl_log import DataLakeSnapshot, EtlLog
from app.models.scoring import AuditLog
from app.models.transaction import Transaction
from app.repositories.etl_repo import DataLakeRepository, EtlRepository
from app.schemas.etl import DataLakeIngestRequest, EtlRunRequest
from fastapi import status as http_status

logger = get_logger(__name__)


class EtlService:
    """ETL pipeline + DataLake ingest — ADMIN only."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._etl_repo = EtlRepository(db)
        self._dl_repo = DataLakeRepository(db)

    # ============================================================
    # ETL Run
    # ============================================================

    def run_etl(self, request: EtlRunRequest, triggered_by: str) -> EtlLog:
        """
        Trigger ETL job cho target_date.
        Ngăn chạy lại nếu đã SUCCESS (idempotency guard — 1 snapshot per day).

        Raises:
            ConflictError: nếu đã có job SUCCESS cho cùng ngày và job_type
        """
        if self._etl_repo.already_ran_today(request.target_date, request.job_type):
            raise ConflictError(
                f"ETL {request.job_type} cho ngày {request.target_date} đã chạy thành công. "
                "Không thể chạy lại để tránh dữ liệu trùng lặp."
            )

        # ---- Tạo EtlLog RUNNING, commit ngay để có job_id persistent ----
        job = EtlLog(
            job_id=str(uuid.uuid4()),
            job_type=request.job_type,
            target_date=request.target_date,
            status="RUNNING",
            triggered_by=triggered_by,
        )
        self._etl_repo.create(job)
        self._db.commit()

        try:
            snapshot = self._do_etl(job, request.target_date)
            job.status = "SUCCESS"
            job.records_out = 1
            job.completed_at = datetime.now(timezone.utc)
            self._db.add(AuditLog(
                log_id=str(uuid.uuid4()),
                event_type="ETL_JOB_TRIGGERED",
                entity_type="EtlLog",
                entity_id=job.job_id,
                actor_user_id=triggered_by,
                detail_json=json.dumps({
                    "job_type": request.job_type,
                    "target_date": str(request.target_date),
                    "records_in": job.records_in,
                }),
            ))
            self._db.commit()

            logger.info(
                "etl_success",
                job_id=job.job_id,
                target_date=str(request.target_date),
                records_in=job.records_in,
            )
        except Exception as exc:
            # Ghi lỗi vào job log — không để exception silent
            job.status = "FAILED"
            job.error_message = str(exc)[:500]
            job.completed_at = datetime.now(timezone.utc)
            self._db.commit()
            logger.error("etl_failed", job_id=job.job_id, error=str(exc))
            raise AppException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"ETL thất bại: {str(exc)[:200]}",
            )

        return job

    def _do_etl(self, job: EtlLog, target_date: date) -> DataLakeSnapshot:
        """
        Thực thi ETL: aggregate transactions → ghi snapshot.
        Gọi trong try/except của run_etl để đảm bảo job.status luôn được cập nhật.
        """
        # ---- Xác định window của target_date (UTC) ----
        day_start = datetime(target_date.year, target_date.month, target_date.day, tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)

        # ---- Đếm transactions theo status ----
        rows = (
            self._db.query(
                Transaction.status,
                func.count(Transaction.txn_id).label("cnt"),
                func.sum(Transaction.amount).label("total_amt"),
                func.avg(Transaction.fraud_score).label("avg_score"),
            )
            .filter(
                Transaction.txn_time >= day_start,
                Transaction.txn_time < day_end,
            )
            .group_by(Transaction.status)
            .all()
        )

        counts: dict = {"APPROVED": 0, "REJECTED": 0, "MANUAL_REVIEW": 0, "PENDING": 0}
        total_amt = Decimal("0")
        total_cnt = 0
        avg_scores: list[float] = []

        for txn_status, cnt, sum_amt, avg_sc in rows:
            counts[txn_status] = counts.get(txn_status, 0) + cnt
            total_cnt += cnt
            if sum_amt:
                total_amt += Decimal(str(sum_amt))
            if avg_sc:
                avg_scores.append(float(avg_sc) * cnt)   # weighted sum

        weighted_avg_score = (
            round(sum(avg_scores) / total_cnt, 4) if total_cnt > 0 else None
        )

        job.records_in = total_cnt

        # ---- Ghi DataLakeSnapshot ----
        snapshot_data = {
            "target_date": target_date.isoformat(),
            "total_transactions": total_cnt,
            "status_breakdown": counts,
            "total_amount": float(total_amt),
            "avg_fraud_score": weighted_avg_score,
            "fraud_rate": round(counts.get("REJECTED", 0) / total_cnt, 4) if total_cnt > 0 else 0.0,
        }

        snapshot = DataLakeSnapshot(
            snapshot_id=str(uuid.uuid4()),
            snapshot_type="DAILY_TXN_SUMMARY",
            snapshot_date=target_date,
            job_id=job.job_id,
            record_count=total_cnt,
            total_amount=float(total_amt),
            data_json=json.dumps(snapshot_data),
            status="ACTIVE",
        )
        self._dl_repo.create(snapshot)
        return snapshot

    def list_jobs(
        self,
        job_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[EtlLog], int]:
        return self._etl_repo.list_jobs(
            job_type=job_type, status=status, page=page, page_size=page_size
        )

    # ============================================================
    # DataLake Ingest
    # ============================================================

    def ingest(self, request: DataLakeIngestRequest, triggered_by: str) -> DataLakeSnapshot:
        """
        Ingest batch records ngoài vào DataLake.
        Không tạo EtlLog (đây là manual ingest, không phải ETL pipeline).
        """
        total_amount = _sum_amount_from_records(request.records)

        snapshot_data = {
            "source": request.source_label,
            "record_count": len(request.records),
            "ingested_by": triggered_by,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }

        snapshot = DataLakeSnapshot(
            snapshot_id=str(uuid.uuid4()),
            snapshot_type="EXTERNAL_INGEST",
            snapshot_date=request.snapshot_date,
            job_id=None,
            source_label=request.source_label,
            record_count=len(request.records),
            total_amount=total_amount,
            data_json=json.dumps(snapshot_data),
            status="ACTIVE",
        )
        self._dl_repo.create(snapshot)
        self._db.commit()

        logger.info(
            "datalake_ingested",
            snapshot_id=snapshot.snapshot_id,
            source=request.source_label,
            records=len(request.records),
        )
        return snapshot

    def list_snapshots(
        self,
        snapshot_type: Optional[str] = None,
        snapshot_date=None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[DataLakeSnapshot], int]:
        return self._dl_repo.list_snapshots(
            snapshot_type=snapshot_type,
            snapshot_date=snapshot_date,
            status=status,
            page=page,
            page_size=page_size,
        )


# ============================================================
# Helpers
# ============================================================

def _sum_amount_from_records(records: list[dict]) -> Optional[float]:
    """
    Cố gắng tổng hợp field 'amount' từ external records.
    Trả None nếu không có field amount hoặc không parse được.
    """
    total = 0.0
    found = False
    for rec in records:
        val = rec.get("amount")
        if val is not None:
            try:
                total += float(val)
                found = True
            except (TypeError, ValueError):
                pass
    return round(total, 2) if found else None
