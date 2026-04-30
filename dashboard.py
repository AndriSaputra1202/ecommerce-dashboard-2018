import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import os

st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="📦",
    layout="wide",
)
HIGHLIGHT = '#E63946'
BASE      = '#457B9D'
PEAK_H    = [11, 13, 14, 15, 16]
PEAK_D    = [0, 1, 2]
C_WD      = '#457B9D'
C_WE      = '#E63946'

# Load Data
BASE_DIR  = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, 'main_data.csv')

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)

    dt_cols = [
        'order_purchase_timestamp', 'order_approved_at',
        'order_delivered_carrier_date', 'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ]
    for c in dt_cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c])

    if 'hour' not in df.columns:
        df['hour'] = df['order_purchase_timestamp'].dt.hour
    if 'day_of_week' not in df.columns:
        df['day_of_week'] = df['order_purchase_timestamp'].dt.day_name()
    if 'day_num' not in df.columns:
        df['day_num'] = df['order_purchase_timestamp'].dt.dayofweek

    delivered = df[df['order_status'] == 'delivered'].copy()
    if 'processing_days' not in delivered.columns:
        delivered = delivered.dropna(
            subset=['order_approved_at', 'order_delivered_carrier_date']
        )
        delivered['processing_days'] = (
            delivered['order_delivered_carrier_date'] - delivered['order_approved_at']
        ).dt.total_seconds() / 86400
        delivered = delivered[delivered['processing_days'] >= 0]

    if 'approved_weekend' not in delivered.columns:
        delivered['approved_weekend'] = delivered['order_approved_at'].dt.dayofweek >= 5
    if 'approval_type' not in delivered.columns:
        delivered['approval_type'] = delivered['approved_weekend'].map(
            {True: 'Akhir Pekan', False: 'Hari Kerja'}
        )

    return df, delivered

orders_2018, delivered = load_data(DATA_PATH)

hourly  = orders_2018.groupby('hour').size().reset_index(name='total_orders')
daily   = (
    orders_2018.groupby(['day_num','day_of_week']).size()
    .reset_index(name='total_orders').sort_values('day_num')
)
heatmap_data = orders_2018.groupby(['day_num','hour']).size().unstack(fill_value=0)
heatmap_data.index = ['Sen','Sel','Rab','Kam','Jum','Sab','Min']

avg_wd      = delivered[~delivered['approved_weekend']]['processing_days'].mean()
avg_we      = delivered[ delivered['approved_weekend']]['processing_days'].mean()
overall_avg = delivered['processing_days'].mean()
diff_pct    = (avg_we - avg_wd) / avg_wd * 100

summary = delivered.groupby('approval_type')['processing_days'].agg(
    rata_rata='mean', median='median', std='std'
).reset_index()

peak_hour    = int(hourly.sort_values('total_orders', ascending=False).iloc[0]['hour'])
best_day     = daily.sort_values('total_orders', ascending=False).iloc[0]
worst_day    = daily.sort_values('total_orders', ascending=False).iloc[-1]
peak_hr_val  = int(hourly.sort_values('total_orders', ascending=False).iloc[0]['total_orders'])
low_hr_val   = int(hourly.sort_values('total_orders').iloc[0]['total_orders'])
med_wd       = float(summary[summary['approval_type']=='Hari Kerja']['median'].values[0])
med_we       = float(summary[summary['approval_type']=='Akhir Pekan']['median'].values[0])
pct_we       = delivered['approved_weekend'].mean() * 100

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("📦 E-Commerce Analytics Dashboard")
st.caption("Analisis pola pembelian & merchant processing time · **Tahun 2018**")
st.divider()

# Metric Cards 
c1, c2, c3, c4 = st.columns(4)
c1.metric("🛒 Total Order 2018",    f"{orders_2018.shape[0]:,}",  "pesanan")
c2.metric("🕐 Jam Puncak",          f"{peak_hour:02d}.00 WIB",    "volume tertinggi")
c3.metric("⏱️ Avg Processing Time", f"{overall_avg:.2f} hari",    "keseluruhan")
delta_label = f"+{diff_pct:.1f}% vs hari kerja"
c4.metric("📊 Selisih Akhir Pekan", f"+{diff_pct:.1f}%",          delta_label,
          delta_color="inverse")

st.divider()


#  Pertanyaan 1

st.subheader("Pertanyaan 1 — Kapan waktu terbaik untuk kampanye promosi?")

fig1, axes = plt.subplots(1, 3, figsize=(20, 5.5))
fig1.patch.set_facecolor('#ffffff')

day_labels = ['Sen','Sel','Rab','Kam','Jum','Sab','Min']
colors_day = [HIGHLIGHT if i in PEAK_D else BASE for i in daily['day_num']]

ax = axes[0]
ax.set_facecolor('#f8f9fa')
ax.bar(day_labels, daily['total_orders'], color=colors_day,
       edgecolor='white', linewidth=0.8, width=0.65, zorder=3)
ax.set_title('Distribusi Order per Hari', fontweight='bold', pad=12, fontsize=12)
ax.set_xlabel('Hari', labelpad=6, fontsize=10)
ax.set_ylabel('Jumlah Order', labelpad=6, fontsize=10)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
ax.spines[['top','right']].set_visible(False)
ax.yaxis.grid(True, color='#e9ecef', linewidth=0.6, zorder=0)
ax.set_axisbelow(True)
for i, val in enumerate(daily['total_orders']):
    ax.text(i, val + 70, f'{val:,}', ha='center', fontsize=7.5, color='#6c757d')

ax = axes[1]
ax.set_facecolor('#f8f9fa')
colors_hour = [HIGHLIGHT if h in PEAK_H else BASE for h in hourly['hour']]
ax.bar(hourly['hour'], hourly['total_orders'], color=colors_hour,
       edgecolor='white', linewidth=0.6, zorder=3)
ax.set_title('Distribusi Order per Jam', fontweight='bold', pad=12, fontsize=12)
ax.set_xlabel('Jam (WIB)', labelpad=6, fontsize=10)
ax.set_ylabel('Jumlah Order', labelpad=6, fontsize=10)
ax.set_xticks(range(0, 24, 2))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
ax.spines[['top','right']].set_visible(False)
ax.yaxis.grid(True, color='#e9ecef', linewidth=0.6, zorder=0)
ax.set_axisbelow(True)
peak_val = int(hourly[hourly['hour'] == 15]['total_orders'].values[0])
ax.annotate('Puncak\n13.00–16.00',
            xy=(15, peak_val), xytext=(19, peak_val - 500),
            arrowprops=dict(arrowstyle='->', color='#6c757d', lw=1.2),
            fontsize=8, color=HIGHLIGHT, fontweight='bold')

ax = axes[2]
sns.heatmap(heatmap_data, ax=ax, cmap='YlOrRd', linewidths=0.25, annot=False,
            cbar_kws={'label': 'Jumlah Order', 'shrink': 0.8})
ax.set_title('Heatmap: Hari × Jam', fontweight='bold', pad=12, fontsize=12)
ax.set_xlabel('Jam', labelpad=6, fontsize=10)
ax.set_ylabel('')
ax.set_xticks(range(0, 24, 2))
ax.set_xticklabels(range(0, 24, 2), fontsize=8)
ax.tick_params(axis='y', labelsize=9)

plt.tight_layout(pad=2.5)
st.pyplot(fig1)
plt.close()

# Insight Pertanyaa 1
col_a, col_b = st.columns(2)
with col_a:
    st.info(f"**📅 Hari Terbaik**\n\n"
            f"**{best_day['day_of_week']}** mencatat order tertinggi dengan "
            f"**{int(best_day['total_orders']):,} order**. "
            f"Senin–Rabu secara konsisten lebih aktif dibanding akhir pekan.")
    st.warning(f"**📉 Waktu Sepi**\n\n"
               f"Pukul **03.00–05.00 dini hari** adalah titik terendah "
               f"(<{low_hr_val:,} order/jam). Akhir pekan turun **25–35%** vs hari kerja.")
with col_b:
    st.success(f"**🕐 Jam Puncak**\n\n"
               f"Pukul **11.00 & 13.00–16.00 WIB** adalah jam tersibuk "
               f"dengan lebih dari **{peak_hr_val:,} order/jam** di titik tertinggi.")
    st.info(f"**🌡️ Pola Heatmap**\n\n"
            f"Zona paling aktif secara konsisten berada di "
            f"**Senin–Rabu × 11.00–16.00**, mengkonfirmasi kedua dimensi sekaligus.")

st.success(
    "✅ **Kesimpulan:** "
    "Waktu terbaik kampanye promosi adalah **Senin–Rabu pukul 11.00–16.00 WIB**. "
    "Hindari pengeluaran iklan besar pada dini hari (00.00–07.00) dan akhir pekan "
    "kecuali ada segmen target khusus."
)

st.divider()

# Pertanyaan 2

st.subheader("Pertanyaan 2 — Apakah processing time 20% lebih lama di akhir pekan?")

fig2, axes2 = plt.subplots(1, 3, figsize=(20, 5.5))
fig2.patch.set_facecolor('#ffffff')

bar_colors = [C_WD if t == 'Hari Kerja' else C_WE for t in summary['approval_type']]
bars = axes2[0].bar(summary['approval_type'], summary['rata_rata'],
                    color=bar_colors, width=0.5, edgecolor='white', linewidth=0.8, zorder=3)
axes2[0].set_facecolor('#f8f9fa')
axes2[0].set_title('Rata-rata Processing Time', fontweight='bold', pad=12, fontsize=12)
axes2[0].set_ylabel('Hari', labelpad=6, fontsize=10)
axes2[0].set_ylim(0, 4.2)
axes2[0].spines[['top','right']].set_visible(False)
axes2[0].yaxis.grid(True, color='#e9ecef', linewidth=0.6, zorder=0)
axes2[0].set_axisbelow(True)
for bar, val in zip(bars, summary['rata_rata']):
    axes2[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.07,
                  f'{val:.2f} hari', ha='center', fontweight='bold', fontsize=11)
axes2[0].axhline(avg_wd * 1.2, color='#6c757d', linestyle='--',
                 linewidth=1.4, label='Threshold +20%')
axes2[0].legend(fontsize=8.5)

plot_data = [
    delivered[delivered['approval_type'] == 'Hari Kerja']['processing_days'].clip(upper=15).values,
    delivered[delivered['approval_type'] == 'Akhir Pekan']['processing_days'].clip(upper=15).values,
]
bp = axes2[1].boxplot(plot_data, labels=['Hari Kerja', 'Akhir Pekan'],
                      patch_artist=True, notch=False,
                      medianprops=dict(color='white', linewidth=2.5),
                      whiskerprops=dict(linewidth=1.2),
                      capprops=dict(linewidth=1.2))
for patch, c in zip(bp['boxes'], [C_WD, C_WE]):
    patch.set_facecolor(c); patch.set_alpha(0.85)
axes2[1].set_facecolor('#f8f9fa')
axes2[1].set_title('Distribusi Processing Time\n(di-clip pada 15 hari)', fontweight='bold', pad=12, fontsize=12)
axes2[1].set_ylabel('Hari', labelpad=6, fontsize=10)
axes2[1].spines[['top','right']].set_visible(False)
axes2[1].yaxis.grid(True, color='#e9ecef', linewidth=0.6, zorder=0)
axes2[1].set_axisbelow(True)

count_data   = delivered['approval_type'].value_counts()
wedge_colors = [C_WD if k == 'Hari Kerja' else C_WE for k in count_data.index]
wedges, texts, autotexts = axes2[2].pie(
    count_data.values, labels=count_data.index,
    autopct='%1.1f%%', colors=wedge_colors,
    startangle=90, explode=[0, 0.06],
    wedgeprops=dict(linewidth=1.5, edgecolor='white')
)
for at in autotexts:
    at.set_fontweight('bold'); at.set_fontsize(11)
axes2[2].set_title('Proporsi Approval\nHari Kerja vs Akhir Pekan', fontweight='bold', pad=12, fontsize=12)

plt.tight_layout(pad=2.5)
st.pyplot(fig2)
plt.close()

# Insight Pertanyaan 2
col_c, col_d = st.columns(2)
with col_c:
    insight_fn = st.error if diff_pct > 20 else st.success
    label_hipotesis = "🚨 Hipotesis Terbukti" if diff_pct > 20 else "✅ Hipotesis Tidak Terbukti"
    insight_fn(
        f"**{label_hipotesis}**\n\n"
        f"Processing time akhir pekan rata-rata **{avg_we:.2f} hari** vs hari kerja "
        f"**{avg_wd:.2f} hari** — selisih **+{diff_pct:.1f}%**, "
        f"{'melampaui' if diff_pct > 20 else 'tidak melampaui'} threshold 20%."
    )
    st.info(
        f"**📦 Outlier Ekstrem**\n\n"
        f"Boxplot menunjukkan outlier akhir pekan lebih padat di rentang "
        f"**6–15 hari**. Kasus keterlambatan ekstrem lebih sering terjadi "
        f"saat approval jatuh di Sabtu–Minggu."
    )
with col_d:
    st.warning(
        f"**📊 Perbandingan Median**\n\n"
        f"Median hari kerja **≈{med_wd:.1f} hari** vs akhir pekan **≈{med_we:.1f} hari**. "
        f"Gap median besar menunjukkan perlambatan dirasakan mayoritas penjual, "
        f"bukan hanya outlier."
    )
    st.success(
        f"**📐 Skala Dampak**\n\n"
        f"Hanya **{pct_we:.1f}%** approval terjadi di akhir pekan, namun "
        f"dampaknya nyata karena volume absolut yang terdampak tetap signifikan."
    )

st.warning(
    f"✅ **Kesimpulan:** "
    f"Hipotesis **terbukti** — Merchant Processing Time rata-rata "
    f"**{diff_pct:.1f}% lebih lama** saat approval di akhir pekan "
    f"({avg_we:.2f} hari vs {avg_wd:.2f} hari). Perlu SLA khusus akhir pekan "
    f"dan integrasi jadwal penjemputan kurir Sabtu–Minggu."
)
st.divider()
st.caption("© 2024 AndriSaputra_CDCC282D6Y1137 · E-Commerce Analytics Dashboard")
