from datetime import datetime
import pandas as pd
import subprocess
import sys
import glob
import os


# Helper timeline
def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


# 1. Cari Semua Data Mentah dari CSV
files = glob.glob('hasil/raw/data_tokopedia_*.csv')
if len(files) == 0:
    raise Exception("Tidak ada file raw ditemukan. Jalankan crawling dulu.")


log(f"Ditemukan {len(files)} file untuk dibersihkan.")


# Buat folder output jika belum ada
if not os.path.exists('hasil/cleaned'):
    os.makedirs('hasil/cleaned')


# LOOPING: Proses setiap file yang ditemukan
for file_path in files:
    file_name = os.path.basename(file_path)
    log(f"--- Memulai Proses: {file_name} ---")
   
    data = pd.read_csv(file_path)
    log(f"Data dimuat: {len(data)} baris")


    # 2. Bersihkan Kolom Harga
    data['Harga'] = (
        data['Harga Sekarang']
        .astype(str)
        .str.replace('Rp', '', regex=False)
        .str.replace('.', '', regex=False)
        .str.replace(',', '', regex=False)
        .str.strip()
    )
    data['Harga'] = pd.to_numeric(data['Harga'], errors='coerce')


    # 3. Bersihkan Kolom Rating
    data['Rating'] = pd.to_numeric(data['Rating'], errors='coerce')


    # 4. Bersihkan Kolom Terjual
    terjual_raw = (
        data['Terjual'].astype(str)
        .str.lower()
        .str.replace(' terjual', '', regex=False)
        .str.replace('+', '', regex=False)
        .str.strip()
    )


    rb_mask = terjual_raw.str.contains('rb', na=False)


    terjual_rb = (
        terjual_raw[rb_mask]
        .str.replace('rb', '', regex=False)
        .str.replace(',', '.', regex=False)
    )
    terjual_rb = pd.to_numeric(terjual_rb, errors='coerce') * 1000


    terjual_non = (
        terjual_raw[~rb_mask]
        .str.replace('.', '', regex=False)
        .str.replace(',', '', regex=False)
    )
    terjual_non = pd.to_numeric(terjual_non, errors='coerce')


    terjual_final = pd.Series(index=data.index, dtype='float')
    terjual_final.loc[rb_mask]  = terjual_rb
    terjual_final.loc[~rb_mask] = terjual_non
    data['Terjual'] = terjual_final.fillna(0)


    # 5. Hapus Duplikat Berdasarkan Nama Produk
    sebelum_dup = len(data)
    data = data.drop_duplicates(subset=['Nama Produk'])
   
    # 6. Ekstrak Berat dari Nama Produk
    gram = data['Nama Produk'].str.extract(r'(?i)(\d+)\s?(?:gram|gr|g)\b')[0].astype(float)
    kg   = data['Nama Produk'].str.extract(r'(?i)(\d+)\s?kg\b')[0].astype(float) * 1000
    data['Berat per Gram'] = gram.fillna(kg)


    # 7. Filter Data Tidak Valid
    sebelum_val = len(data)
    data = data[data['Berat per Gram'].notna()]
    data = data[data['Harga'] > 1000]


    # 8. Hitung Harga per Gram dan Urutkan
    data['Harga per Gram'] = (data['Harga'] / data['Berat per Gram']).round(2)
    data = data.sort_values(by='Harga per Gram')


    # 9. Simpan Hasil Cleaning (Menggunakan nama file asli sebagai referensi)
    output_path = f'hasil/cleaned/cleaned_{file_name}'
    data.to_csv(output_path, index=False)
   
    log(f"Selesai! File disimpan ke: {output_path}")
    log(f"Ringkasan: {sebelum_dup} baris awal -> {len(data)} baris bersih")
    print("-" * 30)


log("Semua file telah berhasil diproses!")


# Jalankan EDA setelah semua selesai
subprocess.run([sys.executable, "eda.py"])