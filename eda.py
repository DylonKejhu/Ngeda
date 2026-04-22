import pandas as pd
import matplotlib.pyplot as plt

print("\nLanjut Ngeda...")

data = pd.read_csv('hasil/cleaned_data_tokopedia.csv')

# contoh: bar chart harga per gram
plt.figure(figsize=(12, 6))
plt.barh(data['Nama Produk'], data['Harga per Gram'])
plt.xlabel('Harga per Gram (Rp)')
plt.title('Perbandingan Harga per Gram Kopi Gayo')
plt.tight_layout()
plt.show()
