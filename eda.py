import pandas as pd
import glob
import os
from datetime import datetime


# Helper log
def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


print("\nLanjut Ngeda Massal...")


# 1. Ambil semua file dari folder cleaned
files = glob.glob('hasil/cleaned/*.csv')


if len(files) == 0:
    # Jika dijalankan lokal dan file yang diupload ada di folder yang sama,
    # sesuaikan pathnya jika perlu
    raise Exception("Tidak ada file di folder hasil/cleaned.")


log(f"Membaca {len(files)} file cleaned...")
list_df = []
for file in files:
    temp_df = pd.read_csv(file)
    list_df.append(temp_df)


# Menggabungkan semua dataframe
df = pd.concat(list_df, ignore_index=True)
log(f"Total data gabungan: {len(df)} baris")


# --- PERBAIKAN TIPE DATA (Sesuai Struktur File Anda) ---


# 1. Bersihkan Diskon (buang % lalu jadi float)
if 'Diskon' in df.columns:
    df['Diskon'] = df['Diskon'].astype(str).str.replace('%', '', regex=False)
    df['Diskon'] = pd.to_numeric(df['Diskon'], errors='coerce').fillna(0)


# 2. Pastikan kolom numerik lainnya benar
# Perhatikan: Nama kolom disesuaikan dengan file CSV Anda
mapping_kolom = {
    'Harga': 'Harga',
    'Terjual': 'Terjual',
    'Berat per Gram': 'Berat per Gram',
    'Harga per Gram': 'Harga per Gram',
    'Rating': 'Rating'
}


for klm in mapping_kolom.values():
    if klm in df.columns:
        df[klm] = pd.to_numeric(df[klm], errors='coerce')


# Hapus data yang benar-benar kosong di kolom kunci agar korelasi tidak nan
df = df.dropna(subset=['Harga', 'Terjual'])


# --- MULAI EDA ---


# 1. Pengaruh Diskon dan Jumlah Pembelian
corr_diskon_jual = df['Diskon'].corr(df['Terjual'], method='spearman')
print(f"\nKekuatan pengaruh diskon terhadap penjualan: {corr_diskon_jual:.2f}")


# 2. Pengaruh Harga dan Jumlah Pembelian
corr_harga_jual = df['Harga'].corr(df['Terjual'], method='spearman')
print(f"Kekuatan pengaruh harga terhadap penjualan: {corr_harga_jual:.2f}")


# 3. Berat produk yang paling sering dibeli
if 'Berat per Gram' in df.columns:
    berat_populer = df.groupby('Berat per Gram')['Terjual'].sum().sort_values(ascending=False)
    print(f"Berat yang paling banyak laku (total unit): {berat_populer.index[0]} Gram")


# 4. Pola harga masing-masing gram (Median)
if 'Berat per Gram' in df.columns:
    pola_harga = df.groupby('Berat per Gram')['Harga'].median().sort_values()
    print("\nMedian harga per kategori berat (10 teratas):")
    print(pola_harga.head(10))


# 5. Top 5 Produk Paling Laris
print("\nTop 5 Produk Paling Laris:")
print(df.nlargest(5, 'Terjual')[['Nama Produk', 'Diskon', 'Harga', 'Terjual']].to_string(index=False))


# 6. Top 5 Produk Paling Sepi
print("\nTop 5 Produk Paling Sepi Peminat:")
print(df.nsmallest(5, 'Terjual')[['Nama Produk', 'Diskon', 'Harga', 'Terjual']].to_string(index=False))


# 7. Hubungan Diskon dan Penjualan (Sampel)
kaitan_diskon = df.nlargest(5, 'Diskon')[['Nama Produk', 'Diskon', 'Harga', 'Terjual']]
print("\nSampel Produk Diskon Tertinggi:")
print(kaitan_diskon.to_string(index=False))


# 8. Ranking Berat Berdasarkan Variasi
if 'Berat per Gram' in df.columns:
    ranking_berat = df['Berat per Gram'].value_counts().head(10)
    print("\nRanking 10 Besar Berat (Variasi Produk Terbanyak):")
    print(ranking_berat)


# 9. 5 Produk Paling Ekonomis
print("\n5 Produk Paling Ekonomis (Best Value):")
print(df.nsmallest(5, 'Harga per Gram')[['Nama Produk', 'Harga per Gram', 'Terjual']].to_string(index=False))


# 10. 5 Produk Paling Mahal
print("\n5 Produk Paling Premium (Harga per Gram Tertinggi):")
print(df.nlargest(5, 'Harga per Gram')[['Nama Produk', 'Harga per Gram', 'Terjual']].to_string(index=False))


log("EDA Terbaru Selesai!")