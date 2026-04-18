import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os

# ─────────────────────────────────────────
# CONFIG & LOAD DATA
# ─────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide"
)

@st.cache_data
def load_data():
    # Ambil lokasi file dashboard.py, lalu cari CSV di folder yang sama
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    df = pd.read_csv(
        os.path.join(base_dir, "main_data.csv"),
        parse_dates=["order_purchase_timestamp"]
    )
    rfm = pd.read_csv(os.path.join(base_dir, "rfm_data.csv"))
    return df, rfm

df_clean, rfm = load_data()

# ─────────────────────────────────────────
# SIDEBAR — FILTER
# ─────────────────────────────────────────
st.sidebar.image(
    "https://sl.bing.net/kD1vtoGg6hw",
    use_container_width=True
)
st.sidebar.title("🔎 Filter Data")

# Filter Rentang Tanggal
min_date = df_clean["order_purchase_timestamp"].min().date()
max_date = df_clean["order_purchase_timestamp"].max().date()

date_range = st.sidebar.date_input(
    "Rentang Waktu Analisis",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)


st.sidebar.markdown("---")
st.sidebar.caption("📊 Data: Olist Brazilian E-Commerce")
st.sidebar.caption("👤 Nanik Erawati_CDCC284D6X2024")

# ─────────────────────────────────────────
# TERAPKAN FILTER
# ─────────────────────────────────────────
if len(date_range) == 2:
    start_date, end_date = date_range
    df_filtered = df_clean[
        (df_clean["order_purchase_timestamp"].dt.date >= start_date) &
        (df_clean["order_purchase_timestamp"].dt.date <= end_date)
    ]
else:
    df_filtered = df_clean.copy()


# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.title("🛒 Brazilian E-Commerce Dashboard")
st.markdown(
    "Analisis performa penjualan, pola waktu pemesanan, dan segmentasi pelanggan "
    "berbasis data **Olist E-Commerce**."
)
st.markdown("---")

# ─────────────────────────────────────────
# SECTION 1 — METRIC CARDS (KPI)
# ─────────────────────────────────────────
st.subheader("📌 Overview Performa")

total_orders   = df_filtered["order_id"].nunique()
total_revenue  = df_filtered["price"].sum()
total_items    = len(df_filtered)
avg_order_val  = df_filtered.groupby("order_id")["price"].sum().mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("🧾 Total Pesanan",    f"{total_orders:,}")
col2.metric("💰 Total Revenue",    f"R${total_revenue:,.0f}")
col3.metric("📦 Total Item Terjual", f"{total_items:,}")
col4.metric("🛍️ Avg. Order Value", f"R${avg_order_val:,.2f}")

st.markdown("---")

# ─────────────────────────────────────────
# SECTION 2 — PERTANYAAN 1: KATEGORI PRODUK
# ─────────────────────────────────────────
st.subheader("📦 Pertanyaan 1: Kategori Produk dengan Volume & Revenue Tertinggi")

product_performance = df_filtered.groupby("product_category_name_english").agg(
    order_count=("order_id", "nunique"),
    revenue=("price", "sum")
).reset_index()

top_n = st.slider("Tampilkan Top N Kategori", min_value=5, max_value=20, value=10, step=1)

top_volume  = product_performance.sort_values("order_count", ascending=False).head(top_n)
top_revenue = product_performance.sort_values("revenue", ascending=False).head(top_n)

fig1, axes1 = plt.subplots(1, 2, figsize=(18, 7))

# Kiri: Volume
colors_vol = ["#0077b6" if i == 0 else "#adb5bd" for i in range(len(top_volume))]
axes1[0].barh(
    top_volume["product_category_name_english"][::-1],
    top_volume["order_count"][::-1],
    color=colors_vol[::-1]
)
axes1[0].set_title(f"Top {top_n} Kategori — Volume Penjualan",
                   fontsize=14, fontweight="bold", pad=15)
axes1[0].set_xlabel("Jumlah Pesanan (Unit)", fontsize=11)
axes1[0].grid(axis="x", linestyle="--", alpha=0.4)
axes1[0].spines[["top", "right"]].set_visible(False)
for i, v in enumerate(top_volume["order_count"][::-1]):
    axes1[0].text(v + 30, i, f"{v:,}", va="center", fontsize=8)

# Kanan: Revenue
colors_rev = ["#e67e22" if i == 0 else "#adb5bd" for i in range(len(top_revenue))]
axes1[1].barh(
    top_revenue["product_category_name_english"][::-1],
    top_revenue["revenue"][::-1],
    color=colors_rev[::-1]
)
axes1[1].set_title(f"Top {top_n} Kategori — Revenue Terbesar",
                   fontsize=14, fontweight="bold", pad=15)
axes1[1].set_xlabel("Total Pendapatan (BRL)", fontsize=11)
axes1[1].grid(axis="x", linestyle="--", alpha=0.4)
axes1[1].spines[["top", "right"]].set_visible(False)
for i, v in enumerate(top_revenue["revenue"][::-1]):
    axes1[1].text(v + 2000, i, f"R${v:,.0f}", va="center", fontsize=8)

plt.suptitle("Performa Kategori Produk: Volume vs Revenue",
             fontsize=16, fontweight="bold", y=1.02)
plt.tight_layout()
st.pyplot(fig1)

with st.expander("📝 Insight Kategori Produk"):
    st.markdown("""
    - **bed_bath_table** memimpin volume penjualan — produk rumah tangga adalah
      penggerak utama transaksi harian.
    - **health_beauty** & **watches_gifts** unggul di sisi revenue karena harga
      per unit yang lebih tinggi.
    - **Implikasi bisnis:** Strategi stok & promosi harus dibedakan antara
      *volume-driven* dan *revenue-driven* kategori.
    """)

st.markdown("---")

# ─────────────────────────────────────────
# SECTION 3 — PERTANYAAN 2: POLA WAKTU
# ─────────────────────────────────────────
st.subheader("⏰ Pertanyaan 2: Jam & Hari Paling Aktif untuk Pemesanan")

df_filtered["order_hour"] = df_filtered["order_purchase_timestamp"].dt.hour
df_filtered["order_day"]  = df_filtered["order_purchase_timestamp"].dt.day_name()

hourly_orders = df_filtered.groupby("order_hour")["order_id"].nunique().reset_index()
hourly_orders.rename(columns={"order_id": "order_count"}, inplace=True)

days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
daily_orders = df_filtered.groupby("order_day")["order_id"].nunique().reindex(days_order).reset_index()
daily_orders.rename(columns={"order_id": "order_count"}, inplace=True)

fig2, axes2 = plt.subplots(1, 2, figsize=(18, 6))

# Kiri: Per Jam
peak_hour   = hourly_orders.loc[hourly_orders["order_count"].idxmax(), "order_hour"]
colors_hour = ["#0077b6" if h == peak_hour else "#adb5bd"
               for h in hourly_orders["order_hour"]]

axes2[0].bar(hourly_orders["order_hour"], hourly_orders["order_count"], color=colors_hour)
axes2[0].set_title("Distribusi Pesanan per Jam", fontsize=14, fontweight="bold", pad=15)
axes2[0].set_xlabel("Jam (00:00–23:00)", fontsize=11)
axes2[0].set_ylabel("Jumlah Pesanan Unik", fontsize=11)
axes2[0].set_xticks(range(0, 24))
axes2[0].grid(axis="y", linestyle="--", alpha=0.4)
axes2[0].spines[["top", "right"]].set_visible(False)
peak_val = hourly_orders.loc[hourly_orders["order_hour"] == peak_hour, "order_count"].values[0]
axes2[0].annotate(
    f"Puncak: {peak_hour:02d}:00",
    xy=(peak_hour, peak_val),
    xytext=(peak_hour + 2, peak_val * 0.95),
    arrowprops=dict(arrowstyle="->", color="black"),
    fontsize=10, color="#0077b6", fontweight="bold"
)

# Kanan: Per Hari
peak_day   = daily_orders.loc[daily_orders["order_count"].idxmax(), "order_day"]
colors_day = ["#e67e22" if d == peak_day else "#adb5bd"
              for d in daily_orders["order_day"]]

axes2[1].bar(daily_orders["order_day"], daily_orders["order_count"], color=colors_day)
axes2[1].set_title("Distribusi Pesanan per Hari", fontsize=14, fontweight="bold", pad=15)
axes2[1].set_xlabel("Hari dalam Seminggu", fontsize=11)
axes2[1].set_ylabel("Jumlah Pesanan Unik", fontsize=11)
axes2[1].grid(axis="y", linestyle="--", alpha=0.4)
axes2[1].spines[["top", "right"]].set_visible(False)
plt.setp(axes2[1].xaxis.get_majorticklabels(), rotation=30, ha="right")

plt.suptitle("Pola Waktu Pemesanan Pelanggan", fontsize=16, fontweight="bold", y=1.02)
plt.tight_layout()
st.pyplot(fig2)

# Heatmap Hari × Jam
st.markdown("##### 🔥 Heatmap Kepadatan Pemesanan (Hari × Jam)")

heatmap_data = df_filtered.groupby(
    ["order_day", "order_hour"]
)["order_id"].nunique().unstack(fill_value=0)
heatmap_data = heatmap_data.reindex(days_order)

fig3, ax3 = plt.subplots(figsize=(16, 5))
sns.heatmap(
    heatmap_data,
    cmap="YlOrRd",
    annot=False,
    linewidths=0.3,
    cbar_kws={"label": "Jumlah Pesanan"},
    ax=ax3
)
ax3.set_title("Heatmap Kepadatan Waktu Pemesanan (Hari × Jam)",
              fontsize=14, fontweight="bold", pad=15)
ax3.set_xlabel("Jam dalam Sehari", fontsize=11)
ax3.set_ylabel("Hari dalam Seminggu", fontsize=11)
plt.tight_layout()
st.pyplot(fig3)

with st.expander("📝 Insight Pola Waktu"):
    st.markdown("""
    - Puncak pemesanan terjadi antara **pukul 10:00–17:00**, dengan jam tertinggi
      di sekitar pukul 14:00–16:00.
    - **Senin & Selasa** adalah hari paling aktif; **Sabtu & Minggu** paling sepi.
    - **Implikasi bisnis:** Jadwalkan flash sale, push notification, dan kampanye
      iklan di rentang jam tersebut untuk memaksimalkan konversi.
    """)

st.markdown("---")

# ─────────────────────────────────────────
# SECTION 4 — ANALISIS RFM
# ─────────────────────────────────────────
st.subheader("👥 Analisis Lanjutan: Segmentasi Pelanggan (RFM)")

segment_colors = {
    "Champions":        "#0077b6",
    "Loyal Customers":  "#00b4d8",
    "Recent Customers": "#90e0ef",
    "Potential Loyalist":"#52b788",
    "Needs Attention":  "#f4a261",
    "At Risk":          "#e63946",
    "Lost High Value":  "#9d0208",
    "Hibernating":      "#adb5bd"
}

# KPI RFM
col_r1, col_r2, col_r3 = st.columns(3)
col_r1.metric("👥 Total Pelanggan Unik", f"{len(rfm):,}")
col_r2.metric("🏆 Champions",
              f"{len(rfm[rfm['segment'] == 'Champions']):,}")
col_r3.metric("⚠️ At Risk + Lost",
              f"{len(rfm[rfm['segment'].isin(['At Risk','Lost High Value'])]):,}")

# Bar Chart Segmen
fig4, axes4 = plt.subplots(1, 2, figsize=(18, 7))

segment_counts = rfm["segment"].value_counts().reset_index()
segment_counts.columns = ["segment", "count"]
seg_colors_bar = [segment_colors.get(s, "#adb5bd")
                  for s in segment_counts["segment"][::-1]]

axes4[0].barh(segment_counts["segment"][::-1],
              segment_counts["count"][::-1],
              color=seg_colors_bar)
axes4[0].set_title("Jumlah Pelanggan per Segmen RFM",
                   fontsize=14, fontweight="bold", pad=15)
axes4[0].set_xlabel("Jumlah Pelanggan", fontsize=11)
axes4[0].grid(axis="x", linestyle="--", alpha=0.4)
axes4[0].spines[["top", "right"]].set_visible(False)
for i, v in enumerate(segment_counts["count"][::-1]):
    axes4[0].text(v + 10, i, f"{v:,}", va="center", fontsize=9)

segment_monetary = rfm.groupby("segment")["monetary"].mean().reset_index()
segment_monetary = segment_monetary.sort_values("monetary", ascending=False)
seg_colors_mon   = [segment_colors.get(s, "#adb5bd")
                    for s in segment_monetary["segment"][::-1]]

axes4[1].barh(segment_monetary["segment"][::-1],
              segment_monetary["monetary"][::-1],
              color=seg_colors_mon)
axes4[1].set_title("Rata-rata Nilai Belanja per Segmen (BRL)",
                   fontsize=14, fontweight="bold", pad=15)
axes4[1].set_xlabel("Rata-rata Monetary (BRL)", fontsize=11)
axes4[1].grid(axis="x", linestyle="--", alpha=0.4)
axes4[1].spines[["top", "right"]].set_visible(False)
for i, v in enumerate(segment_monetary["monetary"][::-1]):
    axes4[1].text(v + 5, i, f"R${v:,.0f}", va="center", fontsize=9)

plt.suptitle("Analisis Segmentasi Pelanggan RFM",
             fontsize=16, fontweight="bold", y=1.02)
plt.tight_layout()
st.pyplot(fig4)

# Scatter Plot Recency vs Monetary
st.markdown("##### 🔵 Sebaran Pelanggan: Recency vs Monetary")

fig5, ax5 = plt.subplots(figsize=(12, 6))
for seg, color in segment_colors.items():
    subset = rfm[rfm["segment"] == seg]
    ax5.scatter(subset["recency"], subset["monetary"],
                c=color, label=seg, alpha=0.5, s=15)
ax5.set_title("Sebaran Pelanggan: Recency vs Monetary",
              fontsize=14, fontweight="bold", pad=15)
ax5.set_xlabel("Recency (hari sejak pembelian terakhir)", fontsize=11)
ax5.set_ylabel("Monetary (Total Belanja, BRL)", fontsize=11)
ax5.legend(title="Segmen", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=9)
ax5.grid(linestyle="--", alpha=0.3)
ax5.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
st.pyplot(fig5)

# Tabel Ringkasan RFM
st.markdown("##### 📋 Ringkasan Statistik per Segmen")

rfm_summary = rfm.groupby("segment").agg(
    Jumlah_Pelanggan=("customer_id", "count"),
    Avg_Recency=("recency", "mean"),
    Avg_Frequency=("frequency", "mean"),
    Avg_Monetary=("monetary", "mean"),
    Total_Revenue=("monetary", "sum")
).round(1).reset_index().sort_values("Total_Revenue", ascending=False)

rfm_summary.columns = [
    "Segmen", "Jml Pelanggan",
    "Avg Recency (hari)", "Avg Frequency",
    "Avg Monetary (BRL)", "Total Revenue (BRL)"
]
st.dataframe(rfm_summary, use_container_width=True)

with st.expander("📝 Insight RFM & Rekomendasi Bisnis"):
    st.markdown("""
    | Segmen | Strategi |
    |--------|----------|
    | **Champions** | Loyalty program, early access produk baru |
    | **Loyal Customers** | Reward poin, referral program |
    | **Recent Customers** | Welcome email series, cross-sell |
    | **Potential Loyalist** | Nudge pembelian kedua, promo bundling |
    | **Needs Attention** | Re-engagement campaign, reminder |
    | **At Risk** | Diskon terbatas waktu, survei kepuasan |
    | **Lost High Value** | Win-back campaign agresif |
    | **Hibernating** | Email reaktivasi atau exclude dari list aktif |
    """)

st.markdown("---")
st.caption("© 2026 · Dicoding Submission · Brazilian E-Commerce Analysis")
