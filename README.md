# Brazilian E-Commerce Dashboard

Dashboard analisis data berbasis Streamlit untuk dataset Olist E-Commerce.

## Cara Menjalankan

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Jalankan dashboard
```bash
streamlit run dashboard/dashboard.py
```

### 3. Buka browser
Otomatis terbuka di `http://localhost:8501`

## Fitur Dashboard

- **KPI Cards** — Total pesanan, revenue, item terjual, avg order value
- **Filter Sidebar** — Rentang tanggal & kategori produk
- **Analisis Kategori** — Top N kategori berdasarkan volume & revenue
- **Pola Waktu** — Bar chart jam/hari + heatmap hari × jam
- **Segmentasi RFM** — Bar chart segmen, scatter plot, tabel ringkasan

## Struktur Folder

```
submission/
├── dashboard/
│   ├── dashboard.py
│   ├── main_data.csv
│   └── rfm_data.csv
├── notebook.ipynb
├── requirements.txt
└── README.md
```