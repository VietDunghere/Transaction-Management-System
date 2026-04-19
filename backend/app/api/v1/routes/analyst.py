from __future__ import annotations
"""
Router: Analyst
GET  /analyst/thresholds                      — xem tất cả threshold hiện tại (ANALYST, MANAGER, ADMIN)
PATCH /analyst/thresholds                     — cập nhật threshold (ANALYST, ADMIN)
GET  /analyst/model-performance/fraud         — thống kê fraud model (ANALYST, MANAGER, ADMIN)
GET  /analyst/model-performance/loan          — thống kê loan model (ANALYST, MANAGER, ADMIN)
GET  /analyst/suppression-rules               — danh sách suppression rules (ANALYST, ADMIN)
POST /analyst/suppression-rules               — tạo suppression rule (ANALYST)
PATCH /analyst/suppression-rules/{id}         — vô hiệu hóa rule (ANALYST, ADMIN)
POST /analyst/reports                         — analyst gửi báo cáo Markdown lên MANAGER (ANALYST)
GET  /analyst/reports                         — danh sách báo cáo (ANALYST, MANAGER, ADMIN)
GET  /analyst/reports/{id}                    — chi tiết báo cáo (ANALYST, MANAGER, ADMIN)
GET  /analyst/reports/{id}/pdf                — tải báo cáo dạng PDF (ANALYST, MANAGER, ADMIN)
PATCH /analyst/reports/{id}/acknowledge       — MANAGER xác nhận báo cáo (MANAGER, ADMIN)
"""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from app.api.v1.deps import require_roles
from app.db.deps import DbSession
from app.schemas.analyst import (
    AnalystReportAcknowledgeRequest,
    AnalystReportCreateRequest,
    AnalystReportResponse,
    AnalystReportSummary,
    FraudModelPerformanceResponse,
    LoanModelPerformanceResponse,
    SuppressionRuleCreateRequest,
    SuppressionRuleResponse,
    ThresholdListResponse,
    ThresholdUpdateRequest,
)
from app.schemas.auth import TokenPayload
from app.services.analyst_service import AnalystService
from app.utils.pdf import render_report_pdf

router = APIRouter(prefix="/analyst", tags=["Analyst"])


@router.get(
    "/thresholds",
    response_model=ThresholdListResponse,
    summary="Xem threshold hiện tại của fraud & loan model",
)
def get_thresholds(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ANALYST", "MANAGER", "ADMIN")),
) -> ThresholdListResponse:
    return AnalystService(db).get_thresholds()


@router.patch(
    "/thresholds",
    response_model=ThresholdListResponse,
    summary="Cập nhật threshold fraud / loan model",
    description="ANALYST hoặc ADMIN có thể điều chỉnh ngưỡng phân loại. Thay đổi ghi vào audit log.",
)
def update_thresholds(
    body: ThresholdUpdateRequest,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ANALYST", "ADMIN")),
) -> ThresholdListResponse:
    return AnalystService(db).update_thresholds(body, actor_user_id=token.sub)


@router.get(
    "/model-performance/fraud",
    response_model=FraudModelPerformanceResponse,
    summary="Thống kê hiệu suất fraud model",
)
def fraud_model_performance(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ANALYST", "MANAGER", "ADMIN")),
    days: int = Query(default=30, ge=1, le=365, description="Số ngày nhìn lại"),
) -> FraudModelPerformanceResponse:
    return AnalystService(db).get_fraud_performance(days=days)


@router.get(
    "/model-performance/loan",
    response_model=LoanModelPerformanceResponse,
    summary="Thống kê hiệu suất loan model",
)
def loan_model_performance(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ANALYST", "MANAGER", "ADMIN")),
    days: int = Query(default=30, ge=1, le=365, description="Số ngày nhìn lại"),
) -> LoanModelPerformanceResponse:
    return AnalystService(db).get_loan_performance(days=days)


@router.get(
    "/suppression-rules",
    response_model=list[SuppressionRuleResponse],
    summary="Danh sách suppression rules",
)
def list_suppression_rules(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ANALYST", "ADMIN")),
    include_inactive: bool = Query(default=False, description="Bao gồm rule đã vô hiệu hóa"),
) -> list[SuppressionRuleResponse]:
    return AnalystService(db).list_suppression_rules(include_inactive=include_inactive)


@router.post(
    "/suppression-rules",
    response_model=SuppressionRuleResponse,
    status_code=201,
    summary="Tạo suppression rule mới",
    description="Tạo rule bypass fraud scoring cho merchant/customer/card cụ thể. Ghi audit log.",
)
def create_suppression_rule(
    body: SuppressionRuleCreateRequest,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ANALYST")),
) -> SuppressionRuleResponse:
    return AnalystService(db).create_suppression_rule(body, actor_user_id=token.sub)


@router.patch(
    "/suppression-rules/{rule_id}",
    response_model=SuppressionRuleResponse,
    summary="Vô hiệu hóa suppression rule",
)
def deactivate_suppression_rule(
    rule_id: str,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ANALYST", "ADMIN")),
) -> SuppressionRuleResponse:
    return AnalystService(db).deactivate_suppression_rule(rule_id, actor_user_id=token.sub)


# ================================================================
# Analyst Reports
# ================================================================

@router.post(
    "/reports",
    response_model=AnalystReportResponse,
    status_code=201,
    summary="Gửi báo cáo / đề xuất lên MANAGER",
    description=(
        "ANALYST soạn báo cáo dạng **Markdown** và submit để MANAGER xem xét. "
        "Báo cáo có thể là phân tích gian lận, đề xuất thay đổi threshold, "
        "hoặc đề xuất suppression rule mới."
    ),
)
def create_analyst_report(
    body: AnalystReportCreateRequest,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ANALYST")),
) -> AnalystReportResponse:
    return AnalystService(db).create_report(body, actor_user_id=token.sub)


@router.get(
    "/reports",
    response_model=dict,
    summary="Danh sách báo cáo của analyst",
)
def list_analyst_reports(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ANALYST", "MANAGER", "ADMIN")),
    status: str | None = Query(default=None, description="Lọc theo trạng thái: PENDING_REVIEW | ACKNOWLEDGED | ARCHIVED"),
    report_type: str | None = Query(default=None),
    submitted_by: str | None = Query(default=None, description="Lọc theo user_id của analyst"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict:
    items, total = AnalystService(db).list_reports(
        status=status,
        report_type=report_type,
        submitted_by=submitted_by,
        limit=limit,
        offset=offset,
    )
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [AnalystReportSummary.model_validate(r).model_dump() for r in items],
    }


@router.get(
    "/reports/{report_id}",
    response_model=AnalystReportResponse,
    summary="Chi tiết báo cáo (bao gồm nội dung Markdown)",
)
def get_analyst_report(
    report_id: str,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ANALYST", "MANAGER", "ADMIN")),
) -> AnalystReportResponse:
    return AnalystService(db).get_report(report_id)


@router.get(
    "/reports/{report_id}/pdf",
    summary="Tải báo cáo dạng PDF",
    description="Render báo cáo Markdown thành file PDF có header/footer chuyên nghiệp.",
    response_class=Response,
    responses={200: {"content": {"application/pdf": {}}, "description": "PDF file"}},
)
def download_analyst_report_pdf(
    report_id: str,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("ANALYST", "MANAGER", "ADMIN")),
) -> Response:
    svc = AnalystService(db)
    report = svc.get_report(report_id)
    submitter_name = (report.submitter.full_name or report.submitter.username) if report.submitter else report.submitted_by
    acknowledger_name = None
    if report.acknowledger:
        acknowledger_name = report.acknowledger.full_name or report.acknowledger.username
    pdf_bytes = render_report_pdf(
        title=report.title,
        report_type=report.report_type,
        content_md=report.content_md,
        status=report.status,
        submitted_at=report.submitted_at,
        submitted_by=submitter_name,
        acknowledged_by=acknowledger_name,
        acknowledged_at=report.acknowledged_at,
        note=report.note,
    )
    filename = f"analyst_report_{report_id[:8]}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.patch(
    "/reports/{report_id}/acknowledge",
    response_model=AnalystReportResponse,
    summary="MANAGER xác nhận đã đọc và xử lý báo cáo",
    description="Chuyển trạng thái báo cáo từ PENDING_REVIEW → ACKNOWLEDGED. Có thể kèm ghi chú phản hồi.",
)
def acknowledge_analyst_report(
    report_id: str,
    body: AnalystReportAcknowledgeRequest,
    db: DbSession,
    token: TokenPayload = Depends(require_roles("MANAGER", "ADMIN")),
) -> AnalystReportResponse:
    return AnalystService(db).acknowledge_report(report_id, body, actor_user_id=token.sub)
