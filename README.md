<div align="center">

# ☕ Coffee Shop Management System

**Hệ thống Quản lý Chuỗi Quán Cà Phê — End-to-End Data Project**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Neon](https://img.shields.io/badge/Neon-Serverless%20Postgres-00E599?style=flat-square&logo=neon&logoColor=black)](https://neon.tech/)
[![Plotly](https://img.shields.io/badge/Plotly-5.20%2B-3F4F75?style=flat-square&logo=plotly&logoColor=white)](https://plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

> Dự án thực hành tổ chức & quản lý dữ liệu cho chuỗi cà phê đa chi nhánh.
> Từ thiết kế schema → seed dữ liệu → stored procedures → dashboard trực quan hóa.

</div>

---

## 📸 Demo Dashboard

> **Dark-theme** analytics dashboard với 5 tab báo cáo, kết nối trực tiếp Neon PostgreSQL.

![Dashboard](docs/screenshots/Dashboard.png)

### Tab 1 — Doanh thu theo Chi nhánh & Tháng

![Revenue Summary](docs/screenshots/tab1_revenue.png)

### Tab 2 — Top Sản phẩm Bán chạy

![Top Products](docs/screenshots/tab2_top_products.png)

### Tab 3 — Phân tích Phương thức Thanh toán

![Payment Methods](docs/screenshots/tab3_payment.png)

### Tab 4 — Loại Đơn hàng theo Chi nhánh

![Order Types](docs/screenshots/tab4_order_type.png)

### Tab 5 — Phân tích Khách hàng

![Customer Analysis](docs/screenshots/tab5_customers.png)

---

## 🗂️ Mục lục

- [Tổng quan dự án](#-tổng-quan-dự-án)
- [Kiến trúc hệ thống](#-kiến-trúc-hệ-thống)
- [Tech Stack](#-tech-stack)
- [Cấu trúc Database](#-cấu-trúc-database)
- [Stored Procedures](#-stored-procedures)
- [Dashboard](#-dashboard)
- [Cài đặt & Chạy](#-cài-đặt--chạy)
- [Cấu trúc thư mục](#-cấu-trúc-thư-mục)

---

## 📋 Tổng quan dự án

Dự án **MDL018** mô phỏng hệ thống quản lý cho một chuỗi quán cà phê với nhiều chi nhánh, bao gồm đầy đủ vòng đời dữ liệu:

| Giai đoạn | Nội dung |
|-----------|----------|
| **Thiết kế** | Schema quan hệ với Table Inheritance (Bảng cha–con) |
| **Xây dựng** | DDL PostgreSQL, constraints, foreign keys |
| **Dữ liệu mẫu** | 5 seed scripts Python tạo dữ liệu thực tế |
| **Phân tích** | 5 Stored Procedures sử dụng ROLLUP, Subquery, PIVOT |
| **Trực quan** | Streamlit dashboard dark-theme với Plotly charts |

**Đặc điểm nổi bật:**
- Áp dụng **Table Inheritance**: `branches → dine_in_branches / delivery_branches`, `employees → fulltime_employees / parttime_employees`
- 5 Stored Procedures kết hợp các kỹ thuật SQL nâng cao: `ROLLUP`, `Subquery lồng`, `PIVOT (CASE WHEN)`
- Dashboard real-time kết nối **Neon Serverless PostgreSQL**, tự làm mới sau 5 phút
- Dark theme nhất quán, bảng màu thân thiện với màn hình

---

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────┐
│                     DATA PIPELINE                        │
│                                                          │
│  dbdiagram.io        Neon Console     TablePlus          │
│  (Schema Design) ──► (DDL Deploy) ──► (DB Management)   │
│                           │                              │
│                     PostgreSQL 16                        │
│                     (Neon Cloud)                         │
│                           │                              │
│              ┌────────────┼────────────┐                 │
│              │            │            │                  │
│         Seed Scripts  Stored Proc  CSV Export            │
│         (Python)      (plpgsql)    (output/)             │
│                            │                             │
│                      Streamlit App                       │
│                      (app.py)                            │
│                      Plotly Charts                       │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Công nghệ |
|-------|-----------|
| **Database** | PostgreSQL 16 (Neon Serverless) |
| **Schema Design** | dbdiagram.io |
| **DB Client** | TablePlus |
| **Backend / ETL** | Python 3.10+, psycopg2, SQLAlchemy |
| **Dashboard** | Streamlit 1.35+ |
| **Charts** | Plotly 5.20+ |
| **Data** | Pandas 2.0+ |
| **Config** | python-dotenv |

---

## 🗄️ Cấu trúc Database

### Sơ đồ Table Inheritance

```
branches (CHA)
├── id, branch_code, address, phone
├── branch_type: dine_in / delivery / hybrid
├── opening_time, closing_time, is_active
│
├── dine_in_branches (CON 1)
│   ├── seating_capacity, number_of_tables, number_of_chairs
│   ├── has_parking, service_charge_percent, has_wifi
│
└── delivery_branches (CON 2)
    ├── delivery_radius_km, base_delivery_fee, free_delivery_min
    ├── max_concurrent_orders, partner_apps

employees (CHA)
├── id, branch_id, full_name, phone, email
├── role: manager / barista / cashier / shipper
├── employee_type: fulltime / parttime
│
├── fulltime_employees (CON 1)
│   ├── monthly_salary, annual_leave_days
│   ├── health_insurance, social_insurance
│   └── contract_start, contract_end, allowance
│
└── parttime_employees (CON 2)
    ├── hourly_rate, max_hours_per_week, min_hours_per_week
    ├── overtime_rate, available_days, preferred_shift

products
└── id, name, category, price, size, is_available

customers
└── id, full_name, phone, email, registered_at

orders (CHA)
├── branch_id → branches
├── customer_id → customers (NULL = khách vãng lai)
├── employee_id → employees
├── order_type: dine_in / takeaway / delivery
└── payment_method: cash / card / momo / bank_transfer

order_items (CON)
└── order_id, product_id, quantity, unit_price, note
```

### Thống kê dữ liệu mẫu

| Bảng | Số bản ghi |
|------|-----------|
| branches | 5 chi nhánh |
| employees | ~25 nhân viên |
| products | ~30 sản phẩm |
| customers | ~50 khách hàng |
| orders | ~500 đơn hàng |
| order_items | ~1,200 dòng |

---

## 📊 Stored Procedures

5 functions PostgreSQL phân tích nghiệp vụ, sử dụng kỹ thuật SQL nâng cao:

### 1. `sp_revenue_by_branch_month(year)` — ROLLUP

Doanh thu từng chi nhánh theo tháng, tự động tính tổng cộng dồn (subtotal + grand total).

```sql
SELECT * FROM sp_revenue_by_branch_month(2025);
-- Trả về: chi_nhanh | loai_chi_nhanh | thang | so_don | doanh_thu
```

**Kỹ thuật:** `GROUP BY ROLLUP(branch_code, month)` — tự sinh dòng tổng mà không cần UNION.

---

### 2. `sp_top_products(start_date, end_date, limit)` — Subquery

Top N sản phẩm bán chạy nhất, so sánh với trung bình hệ thống.

```sql
SELECT * FROM sp_top_products('2025-01-01', '2025-03-31', 10);
-- Trả về: ten_san_pham | danh_muc | so_luong_ban | doanh_thu | so_sanh_tb
```

**Kỹ thuật:** CTE tính `AVG(qty)` toàn hệ thống, sau đó so sánh từng sản phẩm bằng correlated subquery.

---

### 3. `sp_revenue_by_payment_pivot(year)` — PIVOT

Doanh thu mỗi chi nhánh theo từng phương thức thanh toán, dạng bảng ngang.

```sql
SELECT * FROM sp_revenue_by_payment_pivot(2025);
-- Trả về: chi_nhanh | tien_mat | the | momo | chuyen_khoan | tong
```

**Kỹ thuật:** `CASE WHEN payment_method = 'cash' THEN ...` — manual pivot không cần tablefunc extension.

---

### 4. `sp_order_type_by_branch(year)` — Subquery + ROLLUP

Số đơn và tỷ lệ % từng loại đơn (dine_in / takeaway / delivery) theo chi nhánh.

```sql
SELECT * FROM sp_order_type_by_branch(2025);
-- Trả về: chi_nhanh | loai_don | so_don | ty_le_phan_tram | don_tb | so_sanh_tb
```

**Kỹ thuật:** Subquery lồng trong SELECT để tính tỷ lệ %, kết hợp ROLLUP cho dòng tổng.

---

### 5. `sp_customer_analysis(days_back)` — Subquery

Phân loại khách hàng theo tần suất mua và tổng chi tiêu trong N ngày gần nhất.

```sql
SELECT * FROM sp_customer_analysis(90);   -- 90 ngày gần nhất
SELECT * FROM sp_customer_analysis(365);  -- cả năm
```

**Phân loại khách hàng:**

| Phân loại | Tiêu chí |
|-----------|----------|
| **VIP** | ≥ 5 đơn & chi tiêu > 1.5× trung bình |
| **Thân thiết** | ≥ 3 đơn |
| **Thường** | 1–2 đơn |
| **Mới** | Chưa có đơn |

---

## 📈 Dashboard

Dashboard Streamlit với dark theme, 5 tab báo cáo:

| Tab | Nội dung | Charts |
|-----|----------|--------|
| 📊 Doanh thu theo tháng | Grouped bar + Line trend + KPI metrics | Bar, Line, Area |
| 🏆 Top sản phẩm | Horizontal bar + Donut chart danh mục | Bar (H), Pie |
| 💳 Phương thức thanh toán | Stacked bar + Donut PTTT | Bar, Pie |
| 🚚 Loại đơn hàng | Grouped bar + Heatmap tỷ lệ % | Bar, Heatmap, Pie |
| 👥 Khách hàng | Scatter plot + Pie phân loại + Bar top 10 | Scatter, Pie, Bar |

**Tính năng:**
- Sidebar: nhập connection string, chọn năm, khoảng thời gian
- Cache thông minh: tự làm mới sau 5 phút (`@st.cache_data(ttl=300)`)
- Filter tương tác: năm, ngày bắt đầu/kết thúc, top N
- Bảng dữ liệu đầy đủ có thể mở rộng trong từng tab

---

## 🚀 Cài đặt & Chạy

### 1. Yêu cầu

- Python 3.10+
- Tài khoản [Neon](https://neon.tech/) (free tier đủ dùng)
- PostgreSQL client (TablePlus hoặc psql)

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

```
streamlit>=1.35.0
plotly>=5.20.0
pandas>=2.0.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
```

### 3. Tạo database schema

Chạy file SQL lên Neon Console (SQL Editor) hoặc qua TablePlus:

```bash
# Tạo bảng
psql "$DATABASE_URL" -f MDL018_Private-project_Coffee-store.sql

# Tạo stored procedures
psql "$DATABASE_URL" -f stored_procedures.sql
```

### 4. Cấu hình môi trường

Tạo file `.env` trong thư mục `bin/`:

```env
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require
```

> ⚠️ **Không commit file `.env` lên git!** Thêm vào `.gitignore`.

### 5. Seed dữ liệu mẫu

```bash
# Chạy tất cả theo đúng thứ tự
python run_all.py

# Hoặc chạy từng bảng riêng lẻ
python seed_01_branches.py      # Chạy đầu tiên (không phụ thuộc)
python seed_02_employees.py     # Cần branches đã có
python seed_03_products.py      # Không phụ thuộc
python seed_04_customers.py     # Không phụ thuộc
python seed_05_orders.py        # Cần tất cả bảng trên
```

**Thứ tự bắt buộc:**
```
branches → employees → [products, customers] → orders → order_items
```

> ⚠️ Mỗi script **xóa dữ liệu cũ** trước khi tạo mới. Nếu reset `seed_01`, phải chạy lại `seed_02` và `seed_05`.

### 6. Chạy Dashboard

```bash
streamlit run app.py
```

Mở trình duyệt tại `http://localhost:8501`, nhập connection string từ Neon Console → **Connect**.

---

## 📁 Cấu trúc thư mục

```
bin/
├── .env                          ← Connection string (KHÔNG commit)
├── requirements.txt              ← Python dependencies
│
├── MDL018_Private-project_
│   Coffee-store.sql              ← DDL: tạo tất cả bảng + FK
├── stored_procedures.sql         ← 5 stored procedures phân tích
│
├── app.py                        ← Streamlit dashboard (dark theme)
├── utils.py                      ← Helper functions
│
├── run_all.py                    ← Chạy tất cả seed scripts theo thứ tự
├── seed_01_branches.py           ← branches + dine_in_branches + delivery_branches
├── seed_02_employees.py          ← employees + fulltime_employees + parttime_employees
├── seed_03_products.py           ← products
├── seed_04_customers.py          ← customers
├── seed_05_orders.py             ← orders + order_items
│
├── output/                       ← CSV export (dữ liệu đã seed)
│   ├── Branches/
│   ├── Employees/
│   ├── Products/
│   ├── Customers/
│   └── Orders/
│
├── output_raw/                   ← CSV nguồn (dữ liệu thô)
│
└── docs/
    └── screenshots/              ← Ảnh demo dashboard
```

---

## 📝 Ghi chú kỹ thuật

### Table Inheritance vs. Single Table Inheritance
Dự án dùng **Concrete Table Inheritance** (mỗi subtype có bảng riêng) thay vì một bảng lớn, giúp:
- Tránh cột NULL không cần thiết
- Query rõ ràng hơn cho từng loại chi nhánh/nhân viên
- Dễ mở rộng thêm subtype mới

### ROLLUP vs. UNION ALL
`GROUP BY ROLLUP(a, b)` tự sinh subtotal và grand total trong một lần scan,
hiệu năng tốt hơn `UNION ALL` nhiều lần và code gọn hơn.

### Caching Strategy
Dashboard dùng `@st.cache_data(ttl=300)` — cache theo `(db_url, sql_query)`,
tự invalidate sau 5 phút, phù hợp với data warehouse không cần real-time tuyệt đối.

---

<div align="center">

**MDL018 — Data Organization & Management**
*Môn học: Khoa học Dữ liệu*

</div>
