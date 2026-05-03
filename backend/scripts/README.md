# Scripts

## fake_txn_generator.py — Demo Transaction Generator

Script gửi giao dịch fake liên tục vào API để demo hệ thống, tự động seed DB.

### Cách chạy

**Bước 1:** Khởi động API server (terminal 1)
```bash
cd backend
DATABASE_URL=sqlite:///./tms.db uvicorn main:app --reload
```

**Bước 2:** Chạy generator (terminal 2)
```bash
cd backend
python scripts/fake_txn_generator.py
```

### Options

| Flag | Default | Mô tả |
|---|---|---|
| `--url` | `http://localhost:8000` | Base URL của API |
| `--db` | `sqlite:///./tms.db` | Database URL |
| `--rate` | `1.0` | Số giao dịch/giây |
| `--max` | vô hạn | Số giao dịch tối đa rồi dừng |

### Ví dụ

```bash
# 2 giao dịch/giây, dừng sau 100 giao dịch
python scripts/fake_txn_generator.py --rate 2 --max 100

# Chạy vô hạn với PostgreSQL
python scripts/fake_txn_generator.py \
  --db postgresql://tms_user:tms_password@localhost:5432/tms_db \
  --rate 0.5
```

### Các pattern giao dịch

| Pattern | Tỉ lệ | Amount | Thời điểm | Mục đích |
|---|---|---|---|---|
| `😊 normal` | 60% | $5–$150 | Ban ngày | Giao dịch thường ngày |
| `😐 medium` | 25% | $150–$1000 | Ban ngày | Mua sắm lớn |
| `🤔 suspicious` | 10% | $1000–$5000 | Ban đêm | Đáng ngờ |
| `🚨 fraud_like` | 5% | $5000–$50000 | Ban đêm | Gian lận cao |

### Tài khoản mặc định sau khi seed

| Username | Password | Role |
|---|---|---|
| `operator01` | `demo1234` | OPERATOR |
| `reviewer01` | `demo1234` | REVIEWER |
| `manager01` | `demo1234` | MANAGER |
