from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import subprocess
import sys


# 1. Setup Driver (Pastikan chromedriver sesuai dengan versi Chrome kamu)
driver = webdriver.Chrome()

# 2. Buka halaman Tokopedia dengan pencarian spesifik
url = "https://www.tokopedia.com/search?q=kopi%20gayo"
driver.get(url)

# 3. Teknik 'Menunggu' agar satpam tidak curiga dan data muncul semua
# Kita tunggu sampai elemen produk muncul di layar
wait = WebDriverWait(driver, 10)
products = []

try:
    # Scroll perlahan ke bawah agar semua produk ter-load (Lazy Load)
    for i in range(10):
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(2)

    # 4. Mencari elemen produk menggunakan Selector
    # Catatan: Class name bisa berubah sewaktu-waktu (sering diupdate oleh Tokopedia)
    items = driver.find_elements(By.CSS_SELECTOR, 'div[class="css-5wh65g"]')

    if len(items) == 0:
        items = driver.find_elements(By.CSS_SELECTOR, '.css-5466v')
    for item in items:
        try:
            # Menggunakan pencarian berdasarkan atribut data-testid (lebih stabil dari class css-xxx)
            nama = item.find_element(By.CSS_SELECTOR, 'div[class="SzILjt4fxHUFNVT48ZPhHA=="]').text
            harga = item.find_element(By.CSS_SELECTOR, 'div[class="urMOIDHH7I0Iy1Dv2oFaNw== HJhoi0tEIlowsgSNDNWVXg=="]').text
            
            # Untuk rating, kita coba cari elemen yang mengandung teks angka bintang
            try:
                rating = item.find_element(By.CSS_SELECTOR, 'span[class="_2NfJxPu4JC-55aCJ8bEsyw=="]').text
            except:
                rating = "N/A" # Jika tidak ada rating
                
            products.append({
                'Nama Produk': nama,
                'Harga': harga,
                'Rating': rating
            })
        except Exception as e:
            # Skip jika ada satu elemen yang gagal diambil agar tidak menghentikan seluruh proses
            continue

finally:
    # 5. Simpan ke dalam tabel (Pandas) dan tutup browser
    df = pd.DataFrame(products)
    print(df.head())
    df.to_csv('hasil/data_tokopedia.csv', index=False)
    driver.quit()

subprocess.run([sys.executable, "cleaning.py"])