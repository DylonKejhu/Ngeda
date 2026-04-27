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

# 1. Load Data Mentah dari CSV
files = glob.glob('hasil/raw/data_tokopedia_*.csv')
if len(files) == 0:
    raise Exception("Tidak ada file raw ditemukan. Jalankan crawling dulu.")

# Pilih file terbaru berdasarkan tanggal di nama file (DD-MM-YYYY), bukan urutan abjad
def parse_tgl(path):
    nama = os.path.basename(path)                        # data_tokopedia_28-04-2025.csv
    tgl_str = nama.replace('data_tokopedia_', '').replace('.csv', '')
    return datetime.strptime(tgl_str, "%d-%m-%Y")

latest_file = max(files, key=parse_tgl)

data = pd.read_csv(latest_file)
log(f"File terpilih  : {os.path.basename(latest_file)}")
log(f"Data dimuat    : {len(data)} baris")

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
log("Kolom Harga dibersihkan")

# 3. Bersihkan Kolom Rating
data['Rating'] = pd.to_numeric(data['Rating'], errors='coerce')
log("Kolom Rating dibersihkan")

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
log("Kolom Terjual dibersihkan")

# 5. Hapus Duplikat Berdasarkan Nama Produk
sebelum = len(data)
data = data.drop_duplicates(subset=['Nama Produk'])
log(f"Duplikat dihapus: {sebelum - len(data)} baris ({len(data)} tersisa)")

# 6. Ekstrak Berat dari Nama Produk
gram = data['Nama Produk'].str.extract(r'(?i)(\d+)\s?(?:gram|gr|g)\b')[0].astype(float)
kg   = data['Nama Produk'].str.extract(r'(?i)(\d+)\s?kg\b')[0].astype(float) * 1000
data['Berat per Gram'] = gram.fillna(kg)
log("Kolom Berat per Gram diekstrak dari nama produk")

# 7. Filter Data Tidak Valid
sebelum = len(data)
data = data[data['Berat per Gram'].notna()]
data = data[data['Harga'] > 1000]
log(f"Baris tidak valid dibuang: {sebelum - len(data)} baris ({len(data)} tersisa)")

# 8. Hitung Harga per Gram dan Urutkan
data['Harga per Gram'] = (data['Harga'] / data['Berat per Gram']).round(2)
data = data.sort_values(by='Harga per Gram')
log("Harga per Gram dihitung, data diurutkan dari termurah")

# 9. Simpan Hasil Cleaning
if not os.path.exists('hasil/cleaned'):
    os.makedirs('hasil/cleaned')

tgl_hariIni = datetime.now().strftime("%d-%m-%Y")
output_path = f'hasil/cleaned/data_tokopedia_{tgl_hariIni}.csv'
data.to_csv(output_path, index=False)
log(f"Selesai! Clean data tersimpan: {len(data)} baris → {output_path}")
log("Preview 5 baris pertama:")
print(data.head().to_string())

# Jalankan EDA
subprocess.run([sys.executable, "eda.py"])