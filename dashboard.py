import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="E-Commerce Dashboard", page_icon="📦", layout="wide")

# 2. LOAD & PREPROCESS DATA
@st.cache_data
def load_data():
    df = pd.read_csv('main_data.csv')
    
    datetime_columns = [
        'order_purchase_timestamp',
        'order_approved_at',
        'order_delivered_carrier_date'
    ]
    for col in datetime_columns:
        df[col] = pd.to_datetime(df[col])
        
    df['date'] = df['order_purchase_timestamp'].dt.date
    
    df['processing_days'] = (df['order_delivered_carrier_date'] - df['order_approved_at']).dt.total_seconds() / 86400.0
    df['approved_weekend'] = df['order_approved_at'].dt.dayofweek >= 5
    df['approval_type'] = df['approved_weekend'].map({True: 'Akhir Pekan', False: 'Hari Kerja'})
    
    df = df[(df['processing_days'] >= 0) | (df['processing_days'].isna())]
    
    return df

df = load_data()


# SIDEBAR & FILTER
st.sidebar.title("📦 Filter Data")
st.sidebar.markdown("Silakan sesuaikan rentang waktu untuk melihat visualisasi data yang dinamis.")

min_date = df['date'].min()
max_date = df['date'].max()

try:
    start_date, end_date = st.sidebar.date_input(
        "Pilih Rentang Tanggal Pembelian",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
except ValueError:
    st.error("Silakan pilih rentang tanggal yang valid (tanggal awal dan akhir).")
    st.stop()

filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]


# DASHBOARD
st.title("📊 E-Commerce Performance Dashboard")
st.markdown(f"**Menampilkan data dari: `{start_date.strftime('%d %b %Y')}` hingga `{end_date.strftime('%d %b %Y')}`**")
st.markdown("---")

if filtered_df.empty:
    st.warning("Tidak ada data transaksi pada rentang tanggal yang dipilih.")
    st.stop()

# BAGIAN PERTANYAAN 1
st.header("Pertanyaan 1: Kapan waktu terbaik untuk menjalankan kampanye promosi?")

fig_q1, ax_q1 = plt.subplots(figsize=(12, 5))
heatmap_data = filtered_df.groupby(['day_num', 'hour']).size().unstack(fill_value=0)

heatmap_data = heatmap_data.reindex(range(7), fill_value=0)
hari_labels = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min']
heatmap_data.index = hari_labels

sns.heatmap(
    heatmap_data, 
    ax=ax_q1, 
    cmap='YlOrRd', 
    linewidths=0.4, 
    annot=True, 
    fmt='d', 
    annot_kws={'size': 8},
    cbar_kws={'label': 'Jumlah Order'}
)
ax_q1.set_xlabel('Jam (WIB)', fontsize=11)
ax_q1.set_ylabel('Hari', fontsize=11)
st.pyplot(fig_q1)

# Temuan Interaktif Q1
if heatmap_data.values.sum() > 0:
    max_day_name, max_hour = heatmap_data.stack().idxmax()
    max_orders = heatmap_data.max().max()
    total_orders = heatmap_data.values.sum()
    
    st.success(
        f"**Temuan Singkat:** Dari total **{total_orders:,}** data pesanan, waktu terbaik pelanggan melakukan pembelian adalah pada hari **{max_day_name}**, "
        f"tepatnya pada pukul **{max_hour}:00 WIB** (mencapai puncak **{max_orders:,} pesanan**). Menjadwalkan promosi di waktu ini akan menghasilkan tingkat konversi yang paling optimal."
    )
else:
    st.info("Belum cukup data pesanan untuk menemukan waktu puncak pada rentang tanggal ini.")

st.markdown("---")

# BAGIAN PERTANYAAN 2
st.header("Pertanyaan 2: Berapa rata-rata hari proses penjual (Hari Kerja vs Akhir Pekan)?")

delivered_df = filtered_df[filtered_df['order_status'] == 'delivered'].dropna(subset=['processing_days'])

if not delivered_df.empty:
    summary_q2 = delivered_df.groupby('approval_type')['processing_days'].mean().reset_index()
    
    try:
        avg_wkday = summary_q2[summary_q2['approval_type'] == 'Hari Kerja']['processing_days'].values[0]
    except IndexError:
        avg_wkday = 0
        
    try:
        avg_wkend = summary_q2[summary_q2['approval_type'] == 'Akhir Pekan']['processing_days'].values[0]
    except IndexError:
        avg_wkend = 0

    fig_q2, ax_q2 = plt.subplots(figsize=(8, 4))
    sns.barplot(
        x='approval_type', 
        y='processing_days', 
        data=summary_q2, 
        palette={'Hari Kerja': '#457B9D', 'Akhir Pekan': '#E63946'},
        ax=ax_q2
    )
    ax_q2.set_xlabel('Waktu Approval', fontsize=11)
    ax_q2.set_ylabel('Rata-rata Waktu Proses (Hari)', fontsize=11)
    
    for p in ax_q2.patches:
        ax_q2.annotate(format(p.get_height(), '.2f'), 
                       (p.get_x() + p.get_width() / 2., p.get_height()), 
                       ha = 'center', va = 'center', 
                       xytext = (0, 9), 
                       textcoords = 'offset points')
    
    st.pyplot(fig_q2)

    # Temuan Interaktif Q2 
    if avg_wkday > 0 and avg_wkend > 0:
        selisih = ((avg_wkend - avg_wkday) / avg_wkday) * 100
        status_selisih = "lebih lambat" if selisih > 0 else "lebih cepat"
        
        st.success(
            f"**Temuan Singkat:** Dari **{len(delivered_df):,}** data paket sukses, rata-rata penjual membutuhkan **{avg_wkday:.2f} hari** di Hari Kerja "
            f"dan **{avg_wkend:.2f} hari** di Akhir Pekan untuk menyerahkan paket ke kurir. Hal ini menjawab pertanyaan bisnis bahwa proses penyerahan paket menjadi **{abs(selisih):.1f}% {status_selisih}** jika transaksi disetujui pada akhir pekan."
        )
    else:
        st.info("Penyebaran data Hari Kerja atau Akhir Pekan tidak lengkap untuk diperbandingkan pada rentang ini.")
else:
    st.warning("Tidak ada data pesanan berstatus 'delivered' dengan kelengkapan waktu pada rentang tanggal ini.")


# FOOTER

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>© Copyright AndriSaputra_CDCC282D6Y1137</p>", unsafe_allow_html=True)
