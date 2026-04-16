"""
Utility: Haversine Distance
Tính khoảng cách địa lý (km) giữa 2 điểm bằng công thức haversine.
Dùng trong fraud scoring để tính distance_km (customer home vs merchant).
"""

import math


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Tính khoảng cách giữa 2 toạ độ (độ thập phân) theo km.

    Args:
        lat1, lon1: Toạ độ điểm 1 (địa chỉ customers)
        lat2, lon2: Toạ độ điểm 2 (địa chỉ merchant)

    Returns:
        Khoảng cách tính bằng km.
    """
    R = 6371.0  # Bán kính Trái Đất (km)

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lam = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lam / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))
