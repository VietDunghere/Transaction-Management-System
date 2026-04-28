from __future__ import annotations
"""
Pydantic schemas: Lookup
Lightweight schemas cho searchable dropdowns (customer, merchant, channel).
"""

from typing import Optional

from pydantic import BaseModel


class CustomerSearchItem(BaseModel):
    customer_id: str
    full_name: str
    customer_code: str


class MerchantSearchItem(BaseModel):
    merchant_id: str
    merchant_name: str
    merchant_code: str
    merchant_category: Optional[str] = None


class ChannelItem(BaseModel):
    channel_id: int
    channel_name: str
