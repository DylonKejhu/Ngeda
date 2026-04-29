from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import pandas as pd
import subprocess
import sys
import time
import os


# 1. Setup Driver
driver = webdriver.Chrome()


# 2. Buka halaman Tokopedia
url = "https://www.tokopedia.com/search?q=kopi%20gayo"
driver.get(url)


products = []


try:
        # 3. Proses Scroll dan Klik Muat Lebih Banyak
    for i in range(10):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)
        try:
            # Mencari tombol berdasarkan TEKS, ini lebih ampuh daripada class
            load_more_button = driver.find_element(By.CSS_SELECTOR, 'button.css-1turmok-unf-btn.eg8apji0')
           
            # pakai JS click biar lebih reliable
            driver.execute_script("arguments[0].click();", load_more_button)
           
            print(f"Klik 'Muat lebih banyak' ke-{i+1}...")
            time.sleep(5)
        except:
            pass


    # 4. AMBIL SEMUA DATA MENGGUNAKAN CLASS YANG KAMU TEMUKAN
    # Kita gunakan class utama 'css-5wh65g' atau '.css-5466v' sebagai jangkar
    items = driver.find_elements(By.CSS_SELECTOR, '.css-5wh65g, .css-5466v, .css-1asz3by')
    print(f"Total produk terdeteksi: {len(items)}")


    for item in items:
        try:
            # Menggunakan class statis yang kamu temukan sebelumnya
            # Nama Produk
            nama = item.find_element(By.CSS_SELECTOR, 'div[class*="SzILjt"]').text
           
            # Harga Sekarang
            harga_skrg = item.find_element(By.CSS_SELECTOR, 'div[class*="urMOID"]').text
           
            # Harga Sebelum Promo & Diskon (Hanya jika ada)
            try:
                # Cari div yang isinya harga coret
                harga_asli = item.find_element(By.CSS_SELECTOR, 'span[class*="hC1B"]').text
                diskon = item.find_element(By.CSS_SELECTOR, 'span[class*="_7UCY"]').text
            except:
                harga_asli = harga_skrg
                diskon = "0%"


            # Nama Toko & Lokasi (Biasanya ada di dalam container yang sama)
            try:
                # Mencari elemen yang berisi nama toko (biasanya di bawah harga)
                info_toko = item.find_elements(By.CSS_SELECTOR, 'span[class*="si3CNdi"]')
                toko = info_toko[1].text if len(info_toko) > 1 else info_toko[0].text
                lokasi = info_toko[0].text if len(info_toko) > 1 else "N/A"
            except:
                toko = "N/A"
                lokasi = "N/A"


            # Rating & Terjual
            try:
                # Mencari rating (bintang)
                rating = item.find_element(By.CSS_SELECTOR, 'span[class*="_2NfJxPu4JC-55aCJ8bEsyw=="]').text
                # Mencari jumlah terjual
                terjual = item.find_element(By.CSS_SELECTOR, 'span[class*="u6SfjDD2WiBlNW7zHmzRhQ=="]').text
            except:
                rating = "0"
                terjual = "0"


            products.append({
                'Nama Produk': nama,
                'Harga Sekarang': harga_skrg,
                'Harga Asli': harga_asli,
                'Diskon': diskon,
                'Toko': toko,
                'Lokasi': lokasi,
                'Rating': rating,
                'Terjual': terjual
            })
        except:
            continue


finally:
    # 5. Simpan Data
    if not os.path.exists('hasil'):
        os.makedirs('hasil')


    df = pd.DataFrame(products)
    df = df.drop_duplicates()
   
    print(f"Selesai! Berhasil mengambil {len(df)} data produk.")
   
    tgl_hariIni = datetime.now().strftime("%d-%m-%Y")
    df.to_csv(f'hasil/raw/data_tokopedia_{tgl_hariIni}.csv', index=False)
    driver.quit()


# Jalankan script cleaning
subprocess.run([sys.executable, "cleaning.py"])
