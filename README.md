# \# 📦 E-Commerce Analytics Dashboard — 2018

# 

# > Aplikasi analitik berbasis \*\*Streamlit\*\* untuk mengeksplorasi pola transaksi dan efisiensi merchant e-commerce tahun 2018. Dirancang untuk mendukung keputusan bisnis berbasis data.

# 

# \---

# 

# \## ✨ Apa yang Bisa Dilihat?

# 

# | Fitur | Keterangan |

# |---|---|

# | 🛒 Total Order | Jumlah seluruh pesanan tahun 2018 |

# | 🕐 Jam Puncak | Jam dengan volume transaksi tertinggi |

# | ⏱️ Processing Time | Rata-rata waktu pemrosesan merchant |

# | 📊 Selisih Weekend | Perbandingan kecepatan hari kerja vs akhir pekan |

# | 📅 Heatmap Transaksi | Pola aktif berdasarkan hari × jam |

# | 📦 Distribusi Pengiriman | Boxplot \& proporsi approval time |

# 

# \---

# 

# \## 📁 Struktur Proyek

# 

# ```

# submission/

# │

# ├── dashboard/

# │   ├── dashboard.py        ← File utama aplikasi

# │   └── main\_data.csv       

# │

# ├── data/

# │   ├── orders\_dataset.csv

# │   └── order\_items\_dataset.csv

# │

# ├── notebook.ipynb          

# ├── README.md

# ├── requirements.txt

# └── url.txt

# ```

# 

# \---

# 

# \## ⚙️ Persyaratan

# 

# \- Python

# \- pip

# 

# \---

# 

# \## 📦 Instalasi

# 

# \*\*Otomatis:\*\*

# ```bash

# pip install -r requirements.txt

# ```

# 

# \*\*Manual:\*\*

# ```bash

# pip install streamlit pandas matplotlib seaborn numpy

# ```

# 

# \---

# 

# \## ▶️ Menjalankan Dashboard

# 

# ```bash

# \# 1. Masuk ke folder project

# cd submission/dashboard

# 

# \# 2. Jalankan Streamlit

# streamlit run dashboard.py

# ```

# 

# Dashboard akan terbuka di browser → `http://localhost:8501`

# 

# \---

# 

# \## 🌐 Deploy ke Streamlit Cloud

# 

# 1\. Push project ke \*\*GitHub\*\*

# 2\. Buka \[share.streamlit.io](https://share.streamlit.io) dan hubungkan repository

# 3\. Set file utama:

# &#x20;  ```

# &#x20;  dashboard/dashboard.py

# &#x20;  ```

# 4\. Klik \*\*Deploy\*\* — dashboard langsung online!

# 

# \---

# 

# \## ⚠️ Catatan

# 

# \- Pastikan `main\_data.csv` ada di folder `dashboard/`

# \- Gunakan `streamlit run`, \*\*bukan\*\* `python dashboard.py`

# \- Path file menggunakan `os.path.dirname(\_\_file\_\_)` agar aman saat deployment

# 

# \---

# 

# \## 👤 Pengembang

# 

# \*\*Andri Saputra\*\*

# `CDCC282D6Y1137`

# 

# \---

# 

# \*© 2026 · AndriSaputra\_CDCC282D6Y1137 · E-Commerce Analytics Dashboard\*

