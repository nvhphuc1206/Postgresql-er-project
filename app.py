"""
Dashboard trực quan hóa dữ liệu quán cà phê
Chạy: streamlit run app.py
Yêu cầu: pip install streamlit plotly pandas sqlalchemy psycopg2-binary
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
from datetime import date

# ─── Cấu hình trang ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Coffee Store Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS (dark theme) ──────────────────────────────────────────────────
st.markdown("""
<style>
/* Nền tối cho vùng nội dung chính */
[data-testid="stAppViewContainer"] > .main {
    background-color: #0F1117;
}
[data-testid="stHeader"] {
    background-color: #0F1117;
}

/* Metric card */
[data-testid="metric-container"] {
    background-color: #1B2030;
    border: 1px solid #2A3555;
    border-top: 3px solid #3B82F6;
    border-radius: 8px;
    padding: 16px 20px;
}
[data-testid="metric-container"] label {
    color: #94A3B8 !important;
    font-size: 0.85rem !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #E2E8F0 !important;
    font-size: 1.35rem !important;
}

/* Section header */
.section-header {
    font-size: 1rem;
    font-weight: 700;
    color: #CBD5E1;
    border-left: 4px solid #3B82F6;
    padding-left: 10px;
    margin: 20px 0 10px 0;
}

/* Expander */
[data-testid="stExpander"] {
    background-color: #1B2030;
    border: 1px solid #2A3555;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ─── Bảng màu chủ đạo (dark-friendly, không dùng đỏ) ────────────────────────
PALETTE_BRANCH   = ["#60A5FA", "#34D399", "#A78BFA", "#FBBF24", "#38BDF8", "#FB923C"]
PALETTE_CATEGORY = ["#3B82F6", "#10B981", "#8B5CF6", "#F59E0B", "#06B6D4", "#F97316"]
PALETTE_PAYMENT  = ["#60A5FA", "#34D399", "#A78BFA", "#FBBF24"]

CLASSIFICATION_COLORS = {
    "VIP":        "#FBBF24",   # vàng amber
    "Thân thiết": "#34D399",   # xanh lá
    "Thường":     "#60A5FA",   # xanh dương
    "Mới":        "#64748B",   # xám xanh
}
ORDER_TYPE_COLORS = {
    "dine_in":  "#60A5FA",    # xanh dương
    "takeaway": "#FBBF24",    # vàng cam
    "delivery": "#34D399",    # xanh lá (thay đỏ)
}

SUMMARY_LABELS = {
    "** TỔNG CỘNG **", "** TỔNG **",
    "** Cả năm **",    "** Tất cả **", "** Cả danh mục **",
}

# ─── Plotly template chung (dark) ────────────────────────────────────────────
def apply_style(fig: go.Figure, height: int = 400) -> go.Figure:
    fig.update_layout(
        height=height,
        template="plotly_dark",
        paper_bgcolor="#1B2030",
        plot_bgcolor="#161B2E",
        font=dict(family="Segoe UI, Arial", size=12, color="#CBD5E1"),
        title=dict(
            text="",
            x=0,
            font=dict(size=14, color="#E2E8F0", family="Segoe UI, Arial"),
        ),
        legend=dict(
            bgcolor="#1B2030",
            bordercolor="#2A3555",
            borderwidth=1,
            font=dict(size=11, color="#CBD5E1"),
            title_text="",          # ← bỏ tiêu đề legend "undefined"
        ),
        margin=dict(t=45, b=35, l=15, r=15),
        xaxis=dict(
            gridcolor="#2A3555",
            linecolor="#374151",
            tickfont=dict(color="#94A3B8", size=11),
            title_font=dict(color="#94A3B8"),
        ),
        yaxis=dict(
            gridcolor="#2A3555",
            linecolor="#374151",
            tickfont=dict(color="#94A3B8", size=11),
            title_font=dict(color="#94A3B8"),
        ),
    )
    return fig


# ─── Helpers ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner="Đang truy vấn dữ liệu...")
def run_query(url: str, sql: str) -> pd.DataFrame:
    engine = create_engine(url)
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)


def fmt_vnd(value: float) -> str:
    if value >= 1_000_000:
        return f"{value/1_000_000:,.1f} tr ₫"
    return f"{value:,.0f} ₫"


def section(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


# ─── Sidebar ─────────────────────────────────────────────────────────────────
st.sidebar.markdown("# ☕ Coffee Shop Management System Dashboard")
st.sidebar.divider()

db_url = st.sidebar.text_input(
    "🔗 Neon Connection String",
    placeholder="postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require",
    type="password",
    help="Lấy từ Neon Console → Connection Details → Connection string",
)

st.sidebar.divider()
year      = st.sidebar.selectbox("📅 Năm", [2024, 2025, 2026], index=1)
days_back = st.sidebar.slider("📆 Khoảng thời gian (ngày)", 30, 365, 90, step=30)
st.sidebar.divider()
st.sidebar.caption("Dữ liệu tự động làm mới sau 5 phút")

# ─── Kiểm tra kết nối ────────────────────────────────────────────────────────
if not db_url:
    st.markdown("""
    <div style='text-align:center; padding: 60px 20px;'>
        <div style='font-size:4rem'>☕</div>
        <h1 style='color:#60A5FA; margin:12px 0 6px'>Coffee Store Dashboard</h1>
        <p style='color:#94A3B8; font-size:1.05rem'>
            Nhập <b>Connection String</b> từ Neon Console để bắt đầu
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.code(
        "postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require",
        language="text",
    )
    st.stop()

try:
    with create_engine(db_url).connect() as _c:
        _c.execute(text("SELECT 1"))
    st.sidebar.success("✅ Kết nối thành công")
except Exception as _e:
    st.sidebar.error(f"❌ {str(_e)[:100]}")
    st.stop()

# ─── Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Doanh thu theo tháng",
    "🏆 Top sản phẩm",
    "💳 Phương thức thanh toán",
    "🚚 Loại đơn hàng",
    "👥 Khách hàng",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — sp_revenue_by_branch_month
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    try:
        df = run_query(db_url, f"SELECT * FROM sp_revenue_by_branch_month({year})")

        df_detail = df[
            ~df["chi_nhanh"].isin(SUMMARY_LABELS) &
            ~df["thang"].isin(SUMMARY_LABELS)
        ].copy()
        df_detail["thang_label"] = "T" + df_detail["thang"]

        grand = df[df["chi_nhanh"] == "** TỔNG CỘNG **"]

        # KPI
        section("Tổng quan")
        c1, c2, c3 = st.columns(3)
        c1.metric("Tổng doanh thu",      fmt_vnd(grand["doanh_thu"].sum())   if not grand.empty else "—")
        c2.metric("Tổng đơn hoàn thành", f"{int(grand['so_don'].sum()):,}"   if not grand.empty else "—")
        c3.metric("Chi nhánh hoạt động", df_detail["chi_nhanh"].nunique())

        # Grouped bar
        section(f"Doanh thu từng tháng theo chi nhánh — {year}")
        fig1 = px.bar(
            df_detail.sort_values("thang"),
            x="thang_label", y="doanh_thu", color="chi_nhanh",
            barmode="group",
            labels={
                "thang_label": "Tháng",
                "doanh_thu":   "Doanh thu (₫)",
                "chi_nhanh":   "Chi nhánh",
            },
            color_discrete_sequence=PALETTE_BRANCH,
        )
        fig1.update_traces(marker_line_width=0)
        apply_style(fig1, 380)
        st.plotly_chart(fig1, use_container_width=True)

        # Line xu hướng
        section("Xu hướng doanh thu toàn hệ thống")
        monthly = (
            df_detail.groupby("thang_label")["doanh_thu"]
            .sum().reset_index().sort_values("thang_label")
        )
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=monthly["thang_label"], y=monthly["doanh_thu"],
            mode="lines+markers",
            line=dict(color="#60A5FA", width=3),
            marker=dict(size=9, color="#FBBF24", line=dict(color="#60A5FA", width=2)),
            fill="tozeroy",
            fillcolor="rgba(96,165,250,0.12)",
            name="Doanh thu",
        ))
        apply_style(fig2, 300)
        fig2.update_layout(
            showlegend=False,
            yaxis_title="Doanh thu (₫)",
            xaxis_title="Tháng",
        )
        st.plotly_chart(fig2, use_container_width=True)

        with st.expander("📋 Bảng dữ liệu đầy đủ"):
            st.dataframe(df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Lỗi: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — sp_top_products
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    ca, cb, cc = st.columns(3)
    start_date = ca.date_input("Từ ngày",         value=date(year, 1, 1))
    end_date   = cb.date_input("Đến ngày",        value=date(year, 12, 31))
    top_n      = cc.slider("Top N sản phẩm", 5, 20, 10)

    try:
        df = run_query(
            db_url,
            f"SELECT * FROM sp_top_products('{start_date}', '{end_date}', {top_n})",
        )

        col_l, col_r = st.columns([3, 2])

        with col_l:
            section(f"Top {top_n} sản phẩm — số lượng bán")
            fig1 = px.bar(
                df, x="so_luong_ban", y="ten_san_pham", orientation="h",
                color="so_sanh_tb",
                labels={
                    "so_luong_ban": "Số lượng bán",
                    "ten_san_pham": "Sản phẩm",
                    "so_sanh_tb":   "So với TB",
                },
                color_discrete_map={
                    "Trên trung bình": "#34D399",   # xanh lá
                    "Dưới trung bình": "#3B82F6",   # xanh dương đậm (thay đỏ)
                },
            )
            fig1.update_traces(marker_line_width=0)
            fig1.update_layout(yaxis={"categoryorder": "total ascending"})
            apply_style(fig1, 420)
            st.plotly_chart(fig1, use_container_width=True)

        with col_r:
            section("Tỷ trọng theo danh mục")
            by_cat = df.groupby("danh_muc")["doanh_thu"].sum().reset_index()
            fig2 = px.pie(
                by_cat, values="doanh_thu", names="danh_muc",
                color_discrete_sequence=PALETTE_CATEGORY,
                hole=0.42,
                labels={"doanh_thu": "Doanh thu (₫)", "danh_muc": "Danh mục"},
            )
            fig2.update_traces(
                textposition="outside",
                textinfo="label+percent",
                marker=dict(line=dict(color="#161B2E", width=2)),
            )
            apply_style(fig2, 420)
            fig2.update_layout(showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

        with st.expander("📋 Bảng dữ liệu đầy đủ"):
            st.dataframe(df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Lỗi: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — sp_revenue_by_payment_pivot
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    PAYMENT_MAP = {
        "tien_mat":     "Tiền mặt",
        "the":          "Thẻ",
        "momo":         "MoMo",
        "chuyen_khoan": "Chuyển khoản",
    }

    try:
        df        = run_query(db_url, f"SELECT * FROM sp_revenue_by_payment_pivot({year})")
        df_branch = df[df["chi_nhanh"] != "** TỔNG CỘNG **"].copy()
        grand_row = df[df["chi_nhanh"] == "** TỔNG CỘNG **"]

        # KPI thanh toán
        section("Tổng quan")
        if not grand_row.empty:
            kpi_cols = st.columns(len(PAYMENT_MAP))
            for col, (db_col, label) in zip(kpi_cols, PAYMENT_MAP.items()):
                col.metric(label, fmt_vnd(float(grand_row[db_col].iloc[0])))

        col_l, col_r = st.columns([3, 2])

        with col_l:
            section("Doanh thu theo PTTT & chi nhánh")
            df_melt = df_branch.melt(
                id_vars="chi_nhanh",
                value_vars=list(PAYMENT_MAP.keys()),
                var_name="phuong_thuc", value_name="doanh_thu",
            )
            df_melt["phuong_thuc"] = df_melt["phuong_thuc"].map(PAYMENT_MAP)

            fig1 = px.bar(
                df_melt, x="chi_nhanh", y="doanh_thu", color="phuong_thuc",
                labels={
                    "chi_nhanh":   "Chi nhánh",
                    "doanh_thu":   "Doanh thu (₫)",
                    "phuong_thuc": "Phương thức",
                },
                color_discrete_sequence=PALETTE_PAYMENT,
            )
            fig1.update_traces(marker_line_width=0)
            apply_style(fig1, 380)
            st.plotly_chart(fig1, use_container_width=True)

        with col_r:
            section("Tỷ trọng PTTT toàn hệ thống")
            # Tính tổng từ df_branch thay vì dòng ROLLUP để tránh lỗi string mismatch
            totals = {PAYMENT_MAP[c]: float(df_branch[c].sum()) for c in PAYMENT_MAP}
            if sum(totals.values()) > 0:
                fig2 = px.pie(
                    values=list(totals.values()),
                    names=list(totals.keys()),
                    color_discrete_sequence=PALETTE_PAYMENT,
                    hole=0.42,
                )
                fig2.update_traces(
                    textposition="outside",
                    textinfo="label+percent",
                    marker=dict(line=dict(color="#161B2E", width=2)),
                )
                apply_style(fig2, 380)
                fig2.update_layout(showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

        with st.expander("📋 Bảng dữ liệu đầy đủ"):
            st.dataframe(df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Lỗi: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — sp_order_type_by_branch
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    try:
        df = run_query(db_url, f"SELECT * FROM sp_order_type_by_branch({year})")
        df_detail = df[
            ~df["chi_nhanh"].isin(SUMMARY_LABELS) &
            ~df["loai_don"].isin(SUMMARY_LABELS)
        ].copy()

        col_l, col_r = st.columns([3, 2])

        with col_l:
            section("Số đơn theo loại & chi nhánh")
            fig1 = px.bar(
                df_detail, x="chi_nhanh", y="so_don", color="loai_don",
                barmode="group",
                labels={
                    "chi_nhanh": "Chi nhánh",
                    "so_don":    "Số đơn",
                    "loai_don":  "Loại đơn",
                },
                color_discrete_map=ORDER_TYPE_COLORS,
            )
            fig1.update_traces(marker_line_width=0)
            apply_style(fig1, 360)
            st.plotly_chart(fig1, use_container_width=True)

        with col_r:
            section("Tỷ lệ loại đơn toàn hệ thống")
            by_type = df_detail.groupby("loai_don")["so_don"].sum().reset_index()
            fig2 = px.pie(
                by_type, values="so_don", names="loai_don",
                color="loai_don",
                color_discrete_map=ORDER_TYPE_COLORS,
                hole=0.42,
                labels={"so_don": "Số đơn", "loai_don": "Loại đơn"},
            )
            fig2.update_traces(
                textposition="outside",
                textinfo="label+percent",
                marker=dict(line=dict(color="#161B2E", width=2)),
            )
            apply_style(fig2, 360)
            fig2.update_layout(showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

        # Heatmap tỷ lệ %
        if "ty_le_phan_tram" in df_detail.columns:
            section("Tỷ lệ % từng loại đơn theo chi nhánh")
            pivot = df_detail.pivot_table(
                index="chi_nhanh", columns="loai_don",
                values="ty_le_phan_tram", aggfunc="first",
            )
            fig3 = px.imshow(
                pivot, text_auto=".1f",
                labels={"color": "%", "chi_nhanh": "Chi nhánh", "loai_don": "Loại đơn"},
                color_continuous_scale=["#161B2E", "#1D4ED8", "#60A5FA"],
                aspect="auto",
            )
            fig3.update_traces(textfont=dict(size=13, color="#FFFFFF"))
            apply_style(fig3, 260)
            fig3.update_layout(
                coloraxis_colorbar=dict(title="%", tickfont_size=11),
                xaxis_title="Loại đơn",
                yaxis_title="Chi nhánh",
            )
            st.plotly_chart(fig3, use_container_width=True)

        with st.expander("📋 Bảng dữ liệu đầy đủ"):
            st.dataframe(df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Lỗi: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — sp_customer_analysis
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    try:
        df = run_query(db_url, f"SELECT * FROM sp_customer_analysis({days_back})")

        # KPI
        section("Tổng quan")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Tổng khách hàng",  len(df))
        c2.metric("Khách VIP",         len(df[df["phan_loai"] == "VIP"]))
        c3.metric("Có đơn trong kỳ",   len(df[df["so_don"] > 0]))
        c4.metric("Tổng doanh thu",    fmt_vnd(float(df["tong_chi_tieu"].sum())))

        col_l, col_r = st.columns([1, 2])

        with col_l:
            section("Phân loại khách hàng")
            by_class = df["phan_loai"].value_counts().reset_index()
            by_class.columns = ["phan_loai", "count"]
            fig1 = px.pie(
                by_class, values="count", names="phan_loai",
                color="phan_loai",
                color_discrete_map=CLASSIFICATION_COLORS,
                hole=0.48,
                labels={"count": "Số khách", "phan_loai": "Phân loại"},
            )
            fig1.update_traces(
                textposition="outside",
                textinfo="label+percent",
                marker=dict(line=dict(color="#161B2E", width=2)),
            )
            apply_style(fig1, 360)
            fig1.update_layout(showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)

        with col_r:
            section("Tương quan: số đơn vs tổng chi tiêu")
            df_active = df[df["so_don"] > 0].copy()
            fig2 = px.scatter(
                df_active,
                x="so_don", y="tong_chi_tieu",
                color="phan_loai", text="khach_hang",
                size="tong_chi_tieu",
                size_max=28,
                labels={
                    "so_don":        "Số đơn",
                    "tong_chi_tieu": "Tổng chi tiêu (₫)",
                    "phan_loai":     "Phân loại",
                },
                color_discrete_map=CLASSIFICATION_COLORS,
            )
            fig2.update_traces(textposition="top center", textfont_size=8)
            apply_style(fig2, 360)
            st.plotly_chart(fig2, use_container_width=True)

        section("Top 10 khách hàng chi tiêu nhiều nhất")
        top10 = df[df["so_don"] > 0].head(10)
        fig3 = px.bar(
            top10, x="tong_chi_tieu", y="khach_hang", orientation="h",
            color="phan_loai",
            labels={
                "tong_chi_tieu": "Tổng chi tiêu (₫)",
                "khach_hang":    "Khách hàng",
                "phan_loai":     "Phân loại",
            },
            color_discrete_map=CLASSIFICATION_COLORS,
        )
        fig3.update_traces(marker_line_width=0)
        fig3.update_layout(yaxis={"categoryorder": "total ascending"})
        apply_style(fig3, 360)
        st.plotly_chart(fig3, use_container_width=True)

        with st.expander("📋 Bảng dữ liệu đầy đủ"):
            st.dataframe(df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Lỗi: {e}")