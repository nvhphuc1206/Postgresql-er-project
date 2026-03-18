-- ============================================
-- 5 THỦ TỤC THƯỜNG TRÚ (STORED PROCEDURES)
-- HỆ THỐNG QUẢN LÝ QUÁN CÀ PHÊ
-- ============================================
-- Nhu cầu 1: Thống kê doanh thu theo chi nhánh và tháng (ROLLUP)
-- Nhu cầu 2: Top sản phẩm bán chạy nhất theo khoảng thời gian (Subquery)
-- Nhu cầu 3: Doanh thu theo phương thức thanh toán và chi nhánh (PIVOT)
-- Nhu cầu 4: Thống kê hiệu suất nhân viên (Subquery + ROLLUP)
-- Nhu cầu 5: Phân tích khách hàng thân thiết (Subquery)
-- ============================================


-- ============================================
-- NHU CẦU 1: THỐNG KÊ DOANH THU THEO CHI NHÁNH VÀ THÁNG
-- Sử dụng: ROLLUP
-- Mục đích: Xem doanh thu từng chi nhánh theo từng tháng,
--           có tổng theo chi nhánh và tổng toàn bộ.
-- ============================================

DROP FUNCTION IF EXISTS sp_revenue_by_branch_month(INTEGER);

CREATE OR REPLACE FUNCTION sp_revenue_by_branch_month(
    p_year INTEGER DEFAULT EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER
)
RETURNS TABLE (
    chi_nhanh       VARCHAR,
    loai_chi_nhanh  TEXT,
    thang           TEXT,
    so_don          BIGINT,
    doanh_thu       NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COALESCE(b.branch_code, '** TỔNG CỘNG **')            AS chi_nhanh,
        -- NULL cho dòng tổng cộng (ROLLUP), hiện loại chi nhánh cho các dòng còn lại
        CASE WHEN GROUPING(b.branch_code) = 1 THEN NULL
             ELSE MAX(b.branch_type)
        END::TEXT                                               AS loai_chi_nhanh,
        COALESCE(TO_CHAR(o.order_date, 'MM'), '** Cả năm **') AS thang,
        COUNT(o.id)                                             AS so_don,
        COALESCE(SUM(o.total_amount), 0)                       AS doanh_thu
    FROM orders o
    JOIN branches b ON o.branch_id = b.id
    WHERE EXTRACT(YEAR FROM o.order_date) = p_year
      AND o.status = 'completed'
    GROUP BY ROLLUP (b.branch_code, TO_CHAR(o.order_date, 'MM'))
    ORDER BY b.branch_code NULLS LAST, thang NULLS LAST;
END;
$$ LANGUAGE plpgsql;

-- Cách gọi:
-- SELECT * FROM sp_revenue_by_branch_month(2025);
-- SELECT * FROM sp_revenue_by_branch_month();  -- mặc định năm hiện tại


-- ============================================
-- NHU CẦU 2: TOP SẢN PHẨM BÁN CHẠY NHẤT
-- Sử dụng: SUBQUERY (truy vấn lồng)
-- Mục đích: Xem top N sản phẩm bán nhiều nhất trong khoảng thời gian,
--           so sánh với số lượng trung bình của tất cả sản phẩm.
-- ============================================

CREATE OR REPLACE FUNCTION sp_top_products(
    p_start_date DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
    p_end_date   DATE DEFAULT CURRENT_DATE,
    p_limit      INTEGER DEFAULT 10
)
RETURNS TABLE (
    ten_san_pham    VARCHAR,
    danh_muc        VARCHAR,
    so_luong_ban    BIGINT,
    doanh_thu       NUMERIC,
    so_don_chua     BIGINT,
    so_sanh_tb      TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH avg_qty AS (
        SELECT ROUND(AVG(sub.total_qty), 1) AS avg_val
        FROM (
            SELECT SUM(oi2.quantity) AS total_qty
            FROM order_items oi2
            JOIN orders o2 ON oi2.order_id = o2.id
            WHERE o2.order_date >= p_start_date
              AND o2.order_date <  p_end_date + INTERVAL '1 day'
              AND o2.status = 'completed'
            GROUP BY oi2.product_id
        ) sub
    )
    SELECT
        p.name                              AS ten_san_pham,
        p.category                          AS danh_muc,
        SUM(oi.quantity)                    AS so_luong_ban,
        SUM(oi.quantity * oi.unit_price)    AS doanh_thu,
        COUNT(DISTINCT oi.order_id)         AS so_don_chua,
        CASE
            WHEN SUM(oi.quantity) > (SELECT avg_val FROM avg_qty)
            THEN 'Trên trung bình'
            ELSE 'Dưới trung bình'
        END                                 AS so_sanh_tb
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    JOIN products p ON oi.product_id = p.id
    WHERE o.order_date >= p_start_date
      AND o.order_date <  p_end_date + INTERVAL '1 day'
      AND o.status = 'completed'
    GROUP BY p.id, p.name, p.category
    ORDER BY so_luong_ban DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Cách gọi:
-- SELECT * FROM sp_top_products('2025-01-01', '2025-03-31', 5);  -- top 5 Q1/2025
-- SELECT * FROM sp_top_products();  -- top 10, 30 ngày gần nhất


-- ============================================
-- NHU CẦU 3: DOANH THU THEO PHƯƠNG THỨC THANH TOÁN VÀ CHI NHÁNH
-- Sử dụng: PIVOT (crosstab thủ công bằng CASE WHEN)
-- Mục đích: Xem mỗi chi nhánh thu bao nhiêu từ cash, card, momo, bank_transfer
--           dạng bảng ngang dễ đọc.
-- ============================================

CREATE OR REPLACE FUNCTION sp_revenue_by_payment_pivot(
    p_year INTEGER DEFAULT EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER
)
RETURNS TABLE (
    chi_nhanh       VARCHAR,
    tien_mat        NUMERIC,
    the             NUMERIC,
    momo            NUMERIC,
    chuyen_khoan    NUMERIC,
    tong            NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COALESCE(b.branch_code, '** TỔNG CỘNG **')                 AS chi_nhanh,
        -- PIVOT: xoay payment_method từ dọc thành ngang
        COALESCE(SUM(CASE WHEN o.payment_method = 'cash'
                      THEN o.total_amount END), 0)                  AS tien_mat,
        COALESCE(SUM(CASE WHEN o.payment_method = 'card'
                      THEN o.total_amount END), 0)                  AS the,
        COALESCE(SUM(CASE WHEN o.payment_method = 'momo'
                      THEN o.total_amount END), 0)                  AS momo,
        COALESCE(SUM(CASE WHEN o.payment_method = 'bank_transfer'
                      THEN o.total_amount END), 0)                  AS chuyen_khoan,
        COALESCE(SUM(o.total_amount), 0)                            AS tong
    FROM orders o
    JOIN branches b ON o.branch_id = b.id
    WHERE EXTRACT(YEAR FROM o.order_date) = p_year
      AND o.status = 'completed'
    GROUP BY ROLLUP(b.branch_code)
    ORDER BY GROUPING(b.branch_code), tong DESC;
END;
$$ LANGUAGE plpgsql;

-- Cách gọi:
-- SELECT * FROM sp_revenue_by_payment_pivot(2025);
-- SELECT * FROM sp_revenue_by_payment_pivot();


-- ============================================
-- NHU CẦU 4: THỐNG KÊ ĐƠN HÀNG THEO LOẠI VÀ CHI NHÁNH
-- Sử dụng: SUBQUERY + ROLLUP
-- Mục đích: Xem mỗi chi nhánh phục vụ tại chỗ, mang đi, hay giao hàng
--           nhiều hơn, để quyết định mở thêm chỗ ngồi hay tăng đội shipper.
--           Có tổng theo chi nhánh và tổng toàn bộ.
-- ============================================
 
DROP FUNCTION IF EXISTS sp_order_type_by_branch(INTEGER);

CREATE OR REPLACE FUNCTION sp_order_type_by_branch(
    p_year INTEGER DEFAULT EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER
)
RETURNS TABLE (
    chi_nhanh       TEXT,
    loai_chi_nhanh  TEXT,
    loai_don        TEXT,
    so_don          BIGINT,
    doanh_thu       NUMERIC,
    ty_le_phan_tram NUMERIC,
    don_tb          NUMERIC,
    so_sanh_tb      TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        sub.chi_nhanh,
        sub.loai_chi_nhanh,
        sub.loai_don,
        sub.so_don,
        sub.doanh_thu,
        -- Tỷ lệ %: lấy tổng đơn của chi nhánh bằng subquery
        CASE
            WHEN sub.loai_don = '** Tất cả **' OR sub.chi_nhanh = '** TỔNG CỘNG **'
                THEN NULL
            ELSE ROUND(
                sub.so_don::NUMERIC * 100 / NULLIF((
                    SELECT COUNT(o2.id)
                    FROM orders o2
                    JOIN branches b2 ON o2.branch_id = b2.id
                    WHERE b2.branch_code = sub.chi_nhanh
                      AND EXTRACT(YEAR FROM o2.order_date) = p_year
                      AND o2.status = 'completed'
                ), 0),
                1
            )
        END                                             AS ty_le_phan_tram,
        -- Giá trị đơn trung bình của loại đơn tại chi nhánh
        CASE
            WHEN sub.loai_don = '** Tất cả **' OR sub.chi_nhanh = '** TỔNG CỘNG **'
                THEN NULL
            ELSE ROUND(sub.doanh_thu / NULLIF(sub.so_don, 0))
        END                                             AS don_tb,
        -- Subquery: so sánh đơn TB với trung bình toàn hệ thống cùng loại đơn
        CASE
            WHEN sub.loai_don = '** Tất cả **' OR sub.chi_nhanh = '** TỔNG CỘNG **'
                THEN NULL
            WHEN ROUND(sub.doanh_thu / NULLIF(sub.so_don, 0)) > (
                SELECT ROUND(AVG(o5.total_amount))
                FROM orders o5
                WHERE o5.order_type = sub.loai_don
                  AND EXTRACT(YEAR FROM o5.order_date) = p_year
                  AND o5.status = 'completed'
            ) THEN 'Cao hơn TB'
            ELSE 'Thấp hơn TB'
        END                                             AS so_sanh_tb
    FROM (
        -- Truy vấn chính với ROLLUP
        SELECT
            COALESCE(b.branch_code, '** TỔNG CỘNG **')::TEXT    AS chi_nhanh,
            CASE WHEN GROUPING(b.branch_code) = 1 THEN NULL
                 ELSE MAX(b.branch_type)
            END::TEXT                                            AS loai_chi_nhanh,
            COALESCE(o.order_type, '** Tất cả **')::TEXT         AS loai_don,
            COUNT(o.id)                                          AS so_don,
            COALESCE(SUM(o.total_amount), 0)                    AS doanh_thu
        FROM orders o
        JOIN branches b ON o.branch_id = b.id
        WHERE EXTRACT(YEAR FROM o.order_date) = p_year
          AND o.status = 'completed'
        GROUP BY ROLLUP (b.branch_code, o.order_type)
    ) sub
    ORDER BY
        CASE WHEN sub.chi_nhanh = '** TỔNG CỘNG **' THEN 1 ELSE 0 END,
        sub.chi_nhanh,
        CASE WHEN sub.loai_don = '** Tất cả **' THEN 1 ELSE 0 END,
        sub.so_don DESC;
END;
$$ LANGUAGE plpgsql;
 
-- Cách gọi:
-- SELECT * FROM sp_order_type_by_branch(2025);


-- ============================================
-- NHU CẦU 5: PHÂN TÍCH KHÁCH HÀNG THÂN THIẾT
-- Sử dụng: SUBQUERY
-- Mục đích: Phân loại khách hàng theo tần suất và giá trị mua hàng,
--           tìm khách VIP, khách tiềm năng, khách lâu không quay lại.
-- ============================================

CREATE OR REPLACE FUNCTION sp_customer_analysis(
    p_days_back INTEGER DEFAULT 90
)
RETURNS TABLE (
    khach_hang      VARCHAR,
    phone           VARCHAR,
    so_don          BIGINT,
    tong_chi_tieu   NUMERIC,
    don_tb          NUMERIC,
    lan_mua_cuoi    TIMESTAMP,
    phan_loai       TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.full_name                                AS khach_hang,
        c.phone                                    AS phone,
        COUNT(o.id)                                AS so_don,
        COALESCE(SUM(o.total_amount), 0)          AS tong_chi_tieu,
        ROUND(COALESCE(AVG(o.total_amount), 0))   AS don_tb,
        MAX(o.order_date)                          AS lan_mua_cuoi,
        -- Subquery: phân loại dựa trên chi tiêu trung bình trong CÙNG khung thời gian
        CASE
            WHEN COUNT(o.id) = 0 THEN 'Mới'
            WHEN COUNT(o.id) >= 5 AND SUM(o.total_amount) > (
                SELECT AVG(sub.total_spent) * 1.5
                FROM (
                    SELECT SUM(o2.total_amount) AS total_spent
                    FROM orders o2
                    WHERE o2.customer_id IS NOT NULL
                      AND o2.status    = 'completed'
                      AND o2.order_date >= CURRENT_DATE - p_days_back * INTERVAL '1 day'
                    GROUP BY o2.customer_id
                ) sub
            ) THEN 'VIP'
            WHEN COUNT(o.id) >= 3 THEN 'Thân thiết'
            ELSE 'Thường'
        END                                        AS phan_loai
    FROM customers c
    LEFT JOIN orders o ON c.id = o.customer_id
        AND o.status     = 'completed'
        AND o.order_date >= CURRENT_DATE - p_days_back * INTERVAL '1 day'
    GROUP BY c.id, c.full_name, c.phone
    ORDER BY tong_chi_tieu DESC;
END;
$$ LANGUAGE plpgsql;

-- Cách gọi:
-- SELECT * FROM sp_customer_analysis(90);   -- 90 ngày gần nhất
-- SELECT * FROM sp_customer_analysis(365);  -- cả năm
-- SELECT * FROM sp_customer_analysis();     -- mặc định 90 ngày
