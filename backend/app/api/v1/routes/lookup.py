from __future__ import annotations
"""
Router: Lookup (Searchable Dropdowns)
GET /lookup/customers   — tìm khách hàng theo tên/mã
GET /lookup/merchants   — tìm merchant theo tên/mã
GET /lookup/channels    — danh sách kênh giao dịch
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func

from app.api.v1.deps import require_roles
from app.db.deps import DbSession
from app.models.customer import Customer
from app.models.merchant import Channel, Merchant
from app.schemas.auth import TokenPayload
from app.schemas.lookup import ChannelItem, CustomerSearchItem, MerchantSearchItem

router = APIRouter(prefix="/lookup", tags=["Lookup"])


@router.get(
    "/customers",
    response_model=List[CustomerSearchItem],
    summary="Tìm khách hàng",
    description="Tìm khách hàng theo tên hoặc mã khách hàng (tối thiểu 2 ký tự).",
)
def search_customers(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("OPERATOR")),
    q: str = Query(..., min_length=2, description="Từ khoá tìm kiếm (tên hoặc mã KH)"),
    limit: int = Query(default=10, ge=1, le=50),
) -> List[CustomerSearchItem]:
    pattern = f"%{q.lower()}%"
    rows = (
        db.query(Customer)
        .filter(
            (func.lower(Customer.full_name).like(pattern))
            | (func.lower(Customer.customer_code).like(pattern))
        )
        .limit(limit)
        .all()
    )
    return [
        CustomerSearchItem(
            customer_id=c.customer_id,
            full_name=c.full_name or "",
            customer_code=c.customer_code or "",
        )
        for c in rows
    ]


@router.get(
    "/merchants",
    response_model=List[MerchantSearchItem],
    summary="Tìm merchant",
    description="Tìm merchant theo tên hoặc mã merchant (tối thiểu 2 ký tự).",
)
def search_merchants(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("OPERATOR")),
    q: str = Query(..., min_length=2, description="Từ khoá tìm kiếm (tên hoặc mã merchant)"),
    limit: int = Query(default=10, ge=1, le=50),
) -> List[MerchantSearchItem]:
    pattern = f"%{q.lower()}%"
    rows = (
        db.query(Merchant)
        .filter(
            (func.lower(Merchant.merchant_name).like(pattern))
            | (func.lower(Merchant.merchant_code).like(pattern))
        )
        .limit(limit)
        .all()
    )
    return [
        MerchantSearchItem(
            merchant_id=m.merchant_id,
            merchant_name=m.merchant_name,
            merchant_code=m.merchant_code,
            merchant_category=m.merchant_category,
        )
        for m in rows
    ]


@router.get(
    "/channels",
    response_model=List[ChannelItem],
    summary="Danh sách kênh giao dịch",
    description="Trả về toàn bộ kênh giao dịch (POS, ATM, Online, Mobile).",
)
def list_channels(
    db: DbSession,
    token: TokenPayload = Depends(require_roles("OPERATOR", "REVIEWER", "MANAGER", "ANALYST", "ADMIN")),
) -> List[ChannelItem]:
    rows = db.query(Channel).all()
    return [
        ChannelItem(
            channel_id=ch.channel_id,
            channel_name=ch.channel_name,
        )
        for ch in rows
    ]
