from datetime import datetime
import pandas as pd
import glob
import os

# Helper timeline
def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")

# Helper parse tanggal dari nama file cleaned (format: data_tokopedia_DD-MM-YYYY.csv)
def parse_tgl(path):
    nama = os.path.basename(path)
    tgl_str = nama.replace('data_tokopedia_', '').replace('.csv', '')
    try:
        return datetime.strptime(tgl_str, "%d-%m-%Y")
    except ValueError:
        return datetime.min

# 1. Load semua cleaned data
files = glob.glob('hasil/cleaned/data_tokopedia*.csv')

if len(files) == 0:
    raise Exception("Tidak ada data cleaned ditemukan.")

files = sorted(files, key=parse_tgl)

old_file = files[0]
new_file = files[-1]

old = pd.read_csv(old_file)
new = pd.read_csv(new_file)

log(f"Data lama: {os.path.basename(old_file)} ({len(old)} baris)")
log(f"Data baru: {os.path.basename(new_file)} ({len(new)} baris)")

# Fix tipe data
numeric_cols = ['Harga', 'Rating', 'Terjual', 'Harga per Gram']

for col in numeric_cols:
    if col in old.columns:
        old[col] = pd.to_numeric(old[col], errors='coerce')
    if col in new.columns:
        new[col] = pd.to_numeric(new[col], errors='coerce')

if 'Diskon' in new.columns:
    new['Diskon'] = (
        new['Diskon']
        .astype(str)
        .str.replace('%', '', regex=False)
        .str.strip()
    )
    new['Diskon'] = pd.to_numeric(new['Diskon'], errors='coerce')

log("Tipe data diperbaiki")

# 2. Statistik Dasar
def basic_stats(df, label):
    print(f"\n===== Statistik {label} =====")
    print(f"Jumlah Produk      : {len(df)}")
    print(f"Rata-rata Harga    : {df['Harga'].mean():,.0f}")
    print(f"Median Harga       : {df['Harga'].median():,.0f}")
    print(f"Min Harga          : {df['Harga'].min():,.0f}")
    print(f"Max Harga          : {df['Harga'].max():,.0f}")
    print(f"Std Harga          : {df['Harga'].std():,.0f}")
    print(f"Rata-rata Rating   : {df['Rating'].mean():.2f}")
    print(f"Total Terjual      : {df['Terjual'].sum():,.0f}")
    print(f"Rata-rata Harga/Gr : {df['Harga per Gram'].mean():.2f}")

log("Menghitung statistik dasar...")
basic_stats(old, "DATA LAMA")
basic_stats(new, "DATA BARU")

# 3. Top Produk
log("Menyusun top produk...")
print("\n===== Top 5 Termurah (Harga per Gram) =====")
print(new.nsmallest(5, 'Harga per Gram')[['Nama Produk', 'Harga per Gram']].to_string(index=False))

print("\n===== Top 5 Termahal (Harga per Gram) =====")
print(new.nlargest(5, 'Harga per Gram')[['Nama Produk', 'Harga per Gram']].to_string(index=False))

# 4. Produk Paling Laris
print("\n===== Top 5 Produk Terlaris =====")
print(new.nlargest(5, 'Terjual')[['Nama Produk', 'Terjual']].to_string(index=False))

# 5. Distribusi Rating
print("\n===== Distribusi Rating =====")
print(new['Rating'].describe())

# 6. Korelasi
log("Menghitung korelasi...")
print("\n===== Korelasi =====")
corr = new[['Harga', 'Rating', 'Terjual', 'Harga per Gram']].corr()
print(corr)

# 7. Perbandingan Lama vs Baru
log("Membandingkan data lama vs baru...")
print("\n===== PERBANDINGAN LAMA vs BARU =====")

def compare(metric, name):
    old_val = old[metric].mean()
    new_val = new[metric].mean()
    diff = new_val - old_val
    pct = (diff / old_val * 100) if old_val != 0 else 0
    print(f"{name}: {old_val:.2f} → {new_val:.2f} ({diff:+.2f}, {pct:+.2f}%)")

compare('Harga', 'Rata-rata Harga')
compare('Rating', 'Rata-rata Rating')
compare('Terjual', 'Rata-rata Terjual')
compare('Harga per Gram', 'Harga per Gram')

# 8. Analisis Toko
print("\n===== Top Toko (Jumlah Produk) =====")
print(new['Toko'].value_counts().head(5).to_string())

print("\n===== Top Lokasi =====")
print(new['Lokasi'].value_counts().head(5).to_string())

# 9. Analisis Diskon
if 'Diskon' in new.columns:
    print("\n===== Analisis Diskon =====")
    print(f"Rata-rata Diskon: {new['Diskon'].mean():.2f}%")
    print(f"Max Diskon      : {new['Diskon'].max():.2f}%")

# 10. Best Value
log("Menghitung best value & overpriced...")
print("\n===== Best Value Produk =====")
best_value = new.sort_values(by=['Harga per Gram', 'Terjual']).head(10)
print(best_value[['Nama Produk', 'Harga per Gram', 'Terjual']].to_string(index=False))

# 11. Overpriced
print("\n===== Overpriced Produk =====")
overpriced = new.sort_values(by=['Harga per Gram', 'Terjual'], ascending=[False, True]).head(10)
print(overpriced[['Nama Produk', 'Harga per Gram', 'Terjual']].to_string(index=False))

# 12. Insight Tambahan
print("\n===== Insight Tambahan =====")

print("Produk dengan rating tertinggi:")
print(new.nlargest(3, 'Rating')[['Nama Produk', 'Rating']].to_string(index=False))

print("\nProduk dengan penjualan tertinggi:")
print(new.nlargest(3, 'Terjual')[['Nama Produk', 'Terjual']].to_string(index=False))

print("\nHarga vs Penjualan (rata-rata per kuartil):")
bins = pd.qcut(new['Harga'], 4, duplicates='drop')
grouped = new.groupby(bins, observed=True)['Terjual'].mean()
print(grouped.to_string())

print("EDA selesai")