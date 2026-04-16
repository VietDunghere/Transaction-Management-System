"""
Utility: Card Number Hashing
Không bao giờ lưu số thẻ thật vào DB.
SHA256 của cc_num dùng để lookup velocity stats.
"""

import hashlib


def hash_card_number(card_number: str) -> str:
    """
    Hash số thẻ bằng SHA256.
    Input được normalize (loại khoảng trắng/dash) trước khi hash.

    Args:
        card_number: Số thẻ dạng string (đã validated là numeric)

    Returns:
        SHA256 hex string (64 ký tự)
    """
    normalized = card_number.replace(" ", "").replace("-", "")
    return hashlib.sha256(normalized.encode()).hexdigest()


def mask_card_number(card_number: str) -> str:
    """
    Che giấu số thẻ để hiển thị — chỉ giữ 4 số cuối.
    VD: "4111111111111111" → "4111 **** **** 1111"

    Args:
        card_number: Số thẻ dạng string

    Returns:
        Chuỗi đã mask dạng PCI-DSS compliant
    """
    normalized = card_number.replace(" ", "").replace("-", "")
    if len(normalized) < 4:
        return "****"
    first4 = normalized[:4]
    last4 = normalized[-4:]
    middle = "*" * (len(normalized) - 8)
    # Format theo nhóm 4 số
    middle_groups = " ".join(
        ["*" * min(4, len(middle) - i) for i in range(0, len(middle), 4)]
    )
    return f"{first4} {middle_groups} {last4}".strip()
