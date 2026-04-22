import pandas as pd
import subprocess
import sys

# 1. Load Data Mentah dari CSV
data = pd.read_csv('hasil/data_tokopedia.csv')
print(f"\nData berhasil dimuat: {len(data)} baris")

# 2. Bersihkan Kolom Harga (Hapus 'Rp', titik, koma lalu konversi ke int)
data['Harga'] = data['Harga'].str.replace('Rp', '').str.replace('.', '').str.replace(',', '').str.strip().astype(int)

# 3. Bersihkan Kolom Rating (Paksa ke numerik, yang tidak valid jadi NaN)
data['Rating'] = pd.to_numeric(data['Rating'], errors='coerce')

# 4. Hapus Duplikat Berdasarkan Nama Produk
sebelum = len(data)
data = data.drop_duplicates(subset=['Nama Produk'])
print(f"Duplikat dihapus: {sebelum - len(data)} baris")

# 5. Ekstrak Berat dari Nama Produk (prioritas gr krn harga pertama, fallback ke kg)
gram = data['Nama Produk'].str.extract(r'(?i)(\d+)\s?(?:gram|gr|g)\b')[0].astype(float)
kg   = data['Nama Produk'].str.extract(r'(?i)(\d+)\s?kg\b')[0].astype(float) * 1000
data['Berat (Gram)'] = gram.fillna(kg)

# 6. Filter Data yang Tidak Valid (tanpa berat atau harga terlalu kecil)
sebelum = len(data)
data = data[data['Berat (Gram)'].notna()]
data = data[data['Harga'] > 1000]
print(f"Baris tidak valid dibuang: {sebelum - len(data)} baris")

# 7. Hitung Harga per Gram dan Urutkan dari Termurah
data['Harga per Gram'] = (data['Harga'] / data['Berat (Gram)']).round(2)
data = data.sort_values(by='Harga per Gram')

# 8. Simpan Hasil Cleaning ke CSV
data.to_csv('hasil/cleaned_data_tokopedia.csv', index=False)
print(f"Clean data tersimpan: {len(data)} baris")
print(data.head())

subprocess.run([sys.executable, "eda.py"])