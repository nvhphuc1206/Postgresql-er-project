<div align="center">

# ☕ Coffee Shop Management System

**Multi-Branch Coffee Chain Management — End-to-End Data Project**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Neon](https://img.shields.io/badge/Neon-Serverless%20Postgres-00E599?style=flat-square&logo=neon&logoColor=black)](https://neon.tech/)
[![Plotly](https://img.shields.io/badge/Plotly-5.20%2B-3F4F75?style=flat-square&logo=plotly&logoColor=white)](https://plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

> A hands-on data organization & management project for a multi-branch coffee chain.
> Full data lifecycle: schema design → seed data → stored procedures → analytics dashboard.

</div>

---

## 📸 Demo Dashboard

> **Dark-theme** analytics dashboard with 5 report tabs, connected directly to Neon PostgreSQL.

![Dashboard](docs/screenshots/Dashboard.png)

### Tab 1 — Revenue by Branch & Month

![Revenue Summary](docs/screenshots/tab1_revenue.png)

### Tab 2 — Top Selling Products

![Top Products](docs/screenshots/tab2_top_products.png)

### Tab 3 — Payment Method Analysis

![Payment Methods](docs/screenshots/tab3_payment.png)

### Tab 4 — Order Types by Branch

![Order Types](docs/screenshots/tab4_order_type.png)

### Tab 5 — Customer Analysis

![Customer Analysis](docs/screenshots/tab5_customers.png)

---

## 🗂️ Table of Contents

- [Project Overview](#-project-overview)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Database Structure](#-database-structure)
- [Stored Procedures](#-stored-procedures)
- [Dashboard](#-dashboard)
- [Setup & Run](#-setup--run)
- [Directory Structure](#-directory-structure)

---

## 📋 Project Overview

**MDL018** simulates a management system for a multi-branch coffee chain, covering the full data lifecycle:

| Stage | Description |
|-------|-------------|
| **Design** | Relational schema with Table Inheritance (parent–child tables) |
| **Build** | PostgreSQL DDL, constraints, foreign keys |
| **Sample Data** | 5 Python seed scripts generating realistic data |
| **Analysis** | 5 Stored Procedures using ROLLUP, Subquery, PIVOT |
| **Visualization** | Dark-theme Streamlit dashboard with Plotly charts |

**Highlights:**
- Applies **Table Inheritance**: `branches → dine_in_branches / delivery_branches`, `employees → fulltime_employees / parttime_employees`
- 5 Stored Procedures combining advanced SQL techniques: `ROLLUP`, `nested Subquery`, `PIVOT (CASE WHEN)`
- Real-time dashboard connected to **Neon Serverless PostgreSQL**, auto-refreshes every 5 minutes
- Consistent dark theme with screen-friendly color palette

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     DATA PIPELINE                       │
│                                                         │
│  dbdiagram.io        Neon Console     TablePlus         │
│  (Schema Design) ──► (DDL Deploy) ──► (DB Management)   │
│                           │                             │
│                     PostgreSQL 16                       │
│                     (Neon Cloud)                        │
│                           │                             │
│              ┌────────────┼────────────┐                │
│              │            │            │                │
│         Seed Scripts  Stored Proc  CSV Export           │
│         (Python)      (plpgsql)    (output/)            │
│                            │                            │
│                      Streamlit App                      │
│                      (app.py)                           │
│                      Plotly Charts                      │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Database** | PostgreSQL 16 (Neon Serverless) |
| **Schema Design** | dbdiagram.io |
| **DB Client** | TablePlus |
| **Backend / ETL** | Python 3.10+, psycopg2, SQLAlchemy |
| **Dashboard** | Streamlit 1.35+ |
| **Charts** | Plotly 5.20+ |
| **Data** | Pandas 2.0+ |
| **Config** | python-dotenv |

---

## 🗄️ Database Structure

### Table Inheritance Diagram

```
branches (PARENT)
├── id, branch_code, address, phone
├── branch_type: dine_in / delivery / hybrid
├── opening_time, closing_time, is_active
│
├── dine_in_branches (CHILD 1)
│   ├── seating_capacity, number_of_tables, number_of_chairs
│   ├── has_parking, service_charge_percent, has_wifi
│
└── delivery_branches (CHILD 2)
    ├── delivery_radius_km, base_delivery_fee, free_delivery_min
    ├── max_concurrent_orders, partner_apps

employees (PARENT)
├── id, branch_id, full_name, phone, email
├── role: manager / barista / cashier / shipper
├── employee_type: fulltime / parttime
│
├── fulltime_employees (CHILD 1)
│   ├── monthly_salary, annual_leave_days
│   ├── health_insurance, social_insurance
│   └── contract_start, contract_end, allowance
│
└── parttime_employees (CHILD 2)
    ├── hourly_rate, max_hours_per_week, min_hours_per_week
    ├── overtime_rate, available_days, preferred_shift

products
└── id, name, category, price, size, is_available

customers
└── id, full_name, phone, email, registered_at

orders (PARENT)
├── branch_id → branches
├── customer_id → customers (NULL = walk-in customer)
├── employee_id → employees
├── order_type: dine_in / takeaway / delivery
└── payment_method: cash / card / momo / bank_transfer

order_items (CHILD)
└── order_id, product_id, quantity, unit_price, note
```

### Sample Data Statistics

| Table | Records |
|-------|---------|
| branches | 6 branches |
| employees | ~30 employees |
| products | ~20 products |
| customers | ~60 customers |
| orders | ~800 orders |
| order_items | ~1,200+ rows |

---

## 📊 Stored Procedures

5 PostgreSQL functions for business analytics using advanced SQL techniques:

### 1. `sp_revenue_by_branch_month(year)` — ROLLUP

Revenue per branch by month, automatically computing subtotals and grand total.

```sql
SELECT * FROM sp_revenue_by_branch_month(2025);
-- Returns: branch | branch_type | month | order_count | revenue
```

**Technique:** `GROUP BY ROLLUP(branch_code, month)` — generates summary rows without UNION.

---

### 2. `sp_top_products(start_date, end_date, limit)` — Subquery

Top N best-selling products compared against the system average.

```sql
SELECT * FROM sp_top_products('2025-01-01', '2025-03-31', 10);
-- Returns: product_name | category | qty_sold | revenue | order_count | vs_average
```

**Technique:** CTE computes `AVG(qty)` across the system, each product is compared via correlated subquery.

---

### 3. `sp_revenue_by_payment_pivot(year)` — PIVOT

Revenue per branch broken down by payment method in a wide-format table.

```sql
SELECT * FROM sp_revenue_by_payment_pivot(2025);
-- Returns: branch | cash | card | momo | bank_transfer | total
```

**Technique:** `CASE WHEN payment_method = 'cash' THEN ...` — manual pivot without tablefunc extension.

---

### 4. `sp_order_type_by_branch(year)` — Subquery + ROLLUP

Order count and percentage breakdown by order type (dine_in / takeaway / delivery) per branch.

```sql
SELECT * FROM sp_order_type_by_branch(2025);
-- Returns: branch | order_type | order_count | percentage | avg_order_value | vs_average
```

**Technique:** Correlated subquery inside SELECT to compute percentages, combined with ROLLUP for totals.

---

### 5. `sp_customer_analysis(days_back)` — Subquery

Classifies customers by purchase frequency and total spend over the last N days.

```sql
SELECT * FROM sp_customer_analysis(90);   -- last 90 days
SELECT * FROM sp_customer_analysis(365);  -- full year
```

**Customer classification:**

| Tier | Criteria |
|------|----------|
| **VIP** | ≥ 5 orders & spend > 1.5× average |
| **Regular** | ≥ 3 orders |
| **Occasional** | 1–2 orders |
| **New** | No orders yet |

---

## 📈 Dashboard

Streamlit dashboard with dark theme, 5 report tabs:

| Tab | Content | Charts |
|-----|---------|--------|
| 📊 Revenue by Month | Grouped bar + Line trend + KPI metrics | Bar, Line, Area |
| 🏆 Top Products | Horizontal bar + Donut chart by category | Bar (H), Pie |
| 💳 Payment Methods | Stacked bar + Donut by payment type | Bar, Pie |
| 🚚 Order Types | Grouped bar + Percentage heatmap | Bar, Heatmap, Pie |
| 👥 Customers | Scatter plot + Classification pie + Top 10 bar | Scatter, Pie, Bar |

**Features:**
- Sidebar: connection string input, year selector, date range slider
- Smart caching: auto-refresh every 5 minutes (`@st.cache_data(ttl=300)`)
- Interactive filters: year, start/end date, top N
- Expandable full data tables in each tab

---

## 🚀 Setup & Run

### 1. Requirements

- Python 3.10+
- [Neon](https://neon.tech/) account (free tier is sufficient)
- PostgreSQL client (TablePlus or psql)

### 2. Install dependencies

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

### 3. Create database schema

Run the SQL files via Neon Console (SQL Editor) or TablePlus:

```bash
# Create tables
psql "$DATABASE_URL" -f MDL018_Private-project_Coffee-store.sql

# Create stored procedures
psql "$DATABASE_URL" -f stored_procedures.sql
```

### 4. Configure environment

Create a `.env` file in the `bin/` directory:

```env
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require
```

> ⚠️ **Do not commit `.env` to git!** Add it to `.gitignore`.

### 5. Seed sample data

```bash
# Run all in the correct order
python run_all.py

# Or run each script individually
python seed_01_branches.py      # Run first (no dependencies)
python seed_02_employees.py     # Requires branches
python seed_03_products.py      # No dependencies
python seed_04_customers.py     # No dependencies
python seed_05_orders.py        # Requires all tables above
```

**Required order:**
```
branches → employees → [products, customers] → orders → order_items
```

> ⚠️ Each script **deletes existing data** before inserting. If you re-run `seed_01`, you must also re-run `seed_02` and `seed_05`.

### 6. Run the Dashboard

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`, enter the connection string from Neon Console → **Connect**.

---

## 📁 Directory Structure

```
bin/
├── .env                          ← Connection string (DO NOT commit)
├── requirements.txt              ← Python dependencies
│
├── MDL018_Private-project_
│   Coffee-store.sql              ← DDL: create all tables + FK constraints
├── stored_procedures.sql         ← 5 analytics stored procedures
│
├── app.py                        ← Streamlit dashboard (dark theme)
├── utils.py                      ← Shared helper functions
│
├── run_all.py                    ← Run all seed scripts in order
├── seed_01_branches.py           ← branches + dine_in_branches + delivery_branches
├── seed_02_employees.py          ← employees + fulltime_employees + parttime_employees
├── seed_03_products.py           ← products
├── seed_04_customers.py          ← customers
├── seed_05_orders.py             ← orders + order_items
│
├── output/                       ← Seeded CSV exports
│   ├── Branches/
│   ├── Employees/
│   ├── Products/
│   ├── Customers/
│   └── Orders/
│
├── output_raw/                   ← Raw source CSV files
│
└── docs/
    └── screenshots/              ← Dashboard demo screenshots
```

---

## 📝 Technical Notes

### Table Inheritance vs. Single Table Inheritance
This project uses **Concrete Table Inheritance** (each subtype has its own table) rather than one large table, which:
- Avoids unnecessary NULL columns
- Produces cleaner queries per branch/employee type
- Makes it easy to add new subtypes in the future

### ROLLUP vs. UNION ALL
`GROUP BY ROLLUP(a, b)` generates subtotals and grand totals in a single scan,
outperforming multiple `UNION ALL` passes and keeping the code concise.

### Caching Strategy
The dashboard uses `@st.cache_data(ttl=300)` — caches by `(db_url, sql_query)`,
auto-invalidates after 5 minutes, suitable for a data warehouse that doesn't require strict real-time updates.

---

<div align="center">

**MDL018 — Data Organization & Management**
*Personal Project — End-to-End Data Engineering*

</div>
