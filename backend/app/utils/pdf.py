from __future__ import annotations
"""
PDF renderer: Markdown → styled PDF.
Uses fpdf2 + markdown library. Font: Arial Unicode (full Vietnamese support).
"""

from datetime import datetime
from io import BytesIO

import re

import markdown
from fpdf import FPDF
from fpdf.enums import XPos, YPos

_FONT_PATH = "/Library/Fonts/Arial Unicode.ttf"
_REPORT_TYPES_VI = {
    "FRAUD_ANALYSIS": "Phân tích Gian lận",
    "LOAN_ANALYSIS": "Phân tích Tín dụng",
    "THRESHOLD_RECOMMENDATION": "Đề xuất Ngưỡng",
    "SUPPRESSION_REVIEW": "Đánh giá Suppression",
    "GENERAL": "Báo cáo Chung",
}
_STATUS_VI = {
    "PENDING_REVIEW": "Chờ xem xét",
    "ACKNOWLEDGED": "Đã xác nhận",
    "ARCHIVED": "Đã lưu trữ",
}
# Colours
_BLUE  = (26, 82, 160)
_LIGHT = (240, 245, 255)
_GREY  = (150, 150, 150)
_GREEN_BG = (235, 248, 235)
_GREEN_BD = (100, 180, 100)


class _ReportPDF(FPDF):
    def __init__(
        self,
        title: str,
        report_type: str,
        status: str,
        submitted_at: datetime,
        submitted_by: str,
    ) -> None:
        super().__init__()
        self._report_title  = title
        self._report_type   = _REPORT_TYPES_VI.get(report_type, report_type)
        self._report_status = _STATUS_VI.get(status, status)
        self._submitted_at  = submitted_at
        self._submitted_by  = submitted_by
        self._add_fonts()

    def _add_fonts(self) -> None:
        for style in ("", "B", "I", "BI"):
            self.add_font("Arial", style=style, fname=_FONT_PATH)

    # ── Header ────────────────────────────────────────────────────
    def header(self) -> None:
        # Navy bar
        self.set_fill_color(*_BLUE)
        self.rect(0, 0, self.w, 12, style="F")
        self.set_font("Arial", style="B", size=8)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 2)
        self.cell(self.w / 2, 8, "Hệ thống Phân tích Rủi ro và Đánh giá Tài chính", new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.set_font("Arial", style="", size=8)
        self.set_x(self.w - 85)
        self.cell(75, 8, f"Loại: {self._report_type}", align="R",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Light-blue title band
        self.set_fill_color(*_LIGHT)
        self.set_draw_color(200, 215, 245)
        self.rect(0, 12, self.w, 18, style="FD")
        self.set_text_color(*_BLUE)
        self.set_font("Arial", style="B", size=12)
        self.set_xy(12, 13)
        # Single-line truncated title to avoid multi-line overflow in header
        self.cell(self.w - 24, 8, self._report_title[:80], new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Meta row
        self.set_font("Arial", style="", size=7.5)
        self.set_text_color(90, 100, 120)
        date_str = self._submitted_at.strftime("%d/%m/%Y %H:%M") if self._submitted_at else ""
        self.set_x(12)
        self.cell(self.w / 2, 5, f"Ngày gửi: {date_str}", new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.cell(self.w / 2 - 14, 5,
                  f"Người gửi: {self._submitted_by}  |  Trạng thái: {self._report_status}",
                  align="R")

        # Separator
        self.set_y(32)
        self.set_draw_color(*_BLUE)
        self.set_line_width(0.35)
        self.line(10, 32, self.w - 10, 32)
        self.ln(3)
        self.set_text_color(0, 0, 0)
        self.set_line_width(0.2)
        self.set_draw_color(0, 0, 0)

    # ── Footer ────────────────────────────────────────────────────
    def footer(self) -> None:
        self.set_y(-11)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), self.w - 10, self.get_y())
        self.set_font("Arial", style="", size=7)
        self.set_text_color(*_GREY)
        self.set_x(10)
        self.cell(self.w / 2 - 10, 8, "HPTRRĐGTC — Analyst Report  |  Confidential",
                  new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.cell(self.w / 2 - 10, 8, f"Trang {self.page_no()}", align="R")


def render_report_pdf(
    title: str,
    report_type: str,
    content_md: str,
    status: str,
    submitted_at: datetime,
    submitted_by: str = "",
    acknowledged_by: str | None = None,
    acknowledged_at: datetime | None = None,
    note: str | None = None,
) -> bytes:
    """Convert a Markdown analyst report to a styled PDF. Returns raw bytes."""

    html_body = markdown.markdown(
        content_md,
        extensions=["tables", "fenced_code", "nl2br"],
    )
    # nl2br leaves empty <p><br /></p> blocks after </table> — strip them so
    # fpdf2 doesn't render blank lines between the table and the next section.
    html_body = re.sub(r"(</table>)\s*(<p>\s*<br\s*/?>\s*</p>\s*)+", r"\1\n", html_body)

    pdf = _ReportPDF(
        title=title,
        report_type=report_type,
        status=status,
        submitted_at=submitted_at,
        submitted_by=submitted_by,
    )
    pdf.set_margins(left=15, top=10, right=15)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.set_font("Arial", size=11)

    # Render Markdown body
    pdf.write_html(html_body)

    # Acknowledgement block (green box, inline — no forced page break)
    if acknowledged_by and acknowledged_at:
        pdf.ln(5)
        ack_date = acknowledged_at.strftime("%d/%m/%Y %H:%M")
        lines = [f"Đã xác nhận bởi: {acknowledged_by}   |   {ack_date}"]
        if note:
            lines.append(f"Ghi chú: {note}")
        ack_text = "\n".join(lines)

        pdf.set_fill_color(*_GREEN_BG)
        pdf.set_draw_color(*_GREEN_BD)
        pdf.set_font("Arial", size=9)
        pdf.set_text_color(30, 100, 30)
        pdf.multi_cell(0, 6.5, ack_text, border=1, fill=True,
                       new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0, 0, 0)
        pdf.set_draw_color(0, 0, 0)

    # Document metadata (PDF properties only, not rendered on page)
    pdf.set_title(title)
    pdf.set_author(submitted_by)
    pdf.set_creator("HPTRRĐGTC Analyst Module")

    return bytes(pdf.output())
