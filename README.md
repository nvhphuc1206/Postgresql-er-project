# Seed Scripts — Hệ thống Quản lý Quán Cà Phê

## Cài đặt

```bash
pip install psycopg2-binary python-dotenv
```

Tạo file `.env` cùng thư mục:

```
DATABASE_URL=postgresql://neondb_owner:xxx@ep-xxx.aws.neon.tech/neondb?sslmode=require
```

## Cấu trúc thư mục

```
seed_scripts/
├── .env                      ← Tạo file này, chứa connection string
├── db_utils.py               ← Module dùng chung (kết nối, hàm tiện ích)
├── seed_01_branches.py       ← branches + dine_in_branches + delivery_branches
├── seed_02_employees.py      ← employees + fulltime_employees + parttime_employees
├── seed_03_products.py       ← products
├── seed_04_customers.py      ← customers
├── seed_05_orders.py         ← orders + order_items
├── run_all.py                ← Chạy tất cả theo thứ tự
└── README.md
```

## Cách chạy

### Chạy tất cả cùng lúc:

```bash
python run_all.py
```

### Chạy từng bảng riêng lẻ (khi cần reset 1 bảng):

```bash
python seed_01_branches.py      # Chạy đầu tiên
python seed_02_employees.py     # Cần branches đã có
python seed_03_products.py      # Không phụ thuộc
python seed_04_customers.py     # Không phụ thuộc
python seed_05_orders.py        # Cần tất cả bảng trên đã có
```

## Thứ tự bắt buộc

```
seed_01 (branches) → seed_02 (employees) → seed_03 (products) → seed_04 (customers) → seed_05 (orders)
```

seed_03 và seed_04 không phụ thuộc nhau nên chạy trước/sau đều được.
seed_05 cần tất cả bảng trước đó đã có dữ liệu.

## Lưu ý

- Mỗi script sẽ **XÓA dữ liệu cũ** của bảng tương ứng trước khi tạo mới
- Nếu chạy lại seed_01 thì cần chạy lại seed_02 và seed_05 vì FK thay đổi
- File `.env` chứa mật khẩu → **KHÔNG đưa lên GitHub** (thêm vào .gitignore)
