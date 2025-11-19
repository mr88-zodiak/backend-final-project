import pandas as pd
import random


# df = pd.read_excel(".\data_bersih.xlsx")
df = pd.read_excel(".\data_bersih_fix.xlsx")

# # 2. Daftar nama Indonesia umum
# nama_indonesia = [
#     "Ahmad", "Siti", "Budi", "Dewi", "Agus", "Rina", "Yusuf", "Wati", "Andi", "Sri",
#     "Hendra", "Nurul", "Fajar", "Lina", "Rizky", "Tina", "Eka", "Rahma", "Doni", "Maya",
#     "Hadi", "Fitri", "Bayu", "Dian", "Anisa", "Joko", "Ayu", "Taufik", "Nina", "Ridho"
# ]

# # 3. Ganti nilai instruksi dengan nama acak dari daftar
# df["nama"] = df["nama"].apply(lambda x: random.choice(nama_indonesia) if "tolong ganti" in str(x).lower() else x)


# # 4. Simpan hasil ke file baru
# df.to_excel("data_bersih_fix.xlsx", index=False)

# print("✅ File berhasil disimpan sebagai data_bersih_fix.xlsx")

# print(df.head())

# df['status tempat tinggal'] = df['status tempat tinggal'].replace({
#     'punya rumah': 'milik sendiri'})
# df['nama'] = df['nama'].replace(['user'+str(i) for i in range(11,51)], 'tolong ganti dengan nama orang')
# print(df['status tempat tinggal'])

# df.to_excel('data_bersih.xlsx', index=False)


# 2. Daftar nilai acak untuk kolom baru
alamat_sedati = [
    "Sedati Gede", "Sedati Agung", "Betro", "Cemandi", "Banjar Kemuning",
    "Kalanganyar", "Tambak Cemandi", "Pepelegi", "Pabean", "Tambakoso"
]

kondisi_barang = ["Baik", "Sangat baik", "Masih baru", "Agak kurang baik"]

kategori = ["Pakaian", "Elektronik", "Furniture", "Peralatan dapur", "Buku"]

# 3. Tambahkan kolom baru dengan nilai acak
df["alamat"] = [random.choice(alamat_sedati) for _ in range(len(df))]
df["kondisi_barang"] = [random.choice(kondisi_barang) for _ in range(len(df))]
df["kategori"] = [random.choice(kategori) for _ in range(len(df))]

# 4. Simpan ke file baru
df.to_excel("data_bersih_lengkap.xlsx", index=False)

print("✅ File berhasil disimpan sebagai data_bersih_lengkap.xlsx dengan kolom baru.")



