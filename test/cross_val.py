import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import numpy as np
import matplotlib.pyplot as plt

# === 1. Baca dan normalisasi huruf ===
dataset = pd.read_excel('./data_bersih_sinkron.xlsx')
dataset = dataset.drop('kondisi_barang', axis=1)
for col in dataset.select_dtypes(include='object').columns:
    dataset[col] = dataset[col].str.lower().str.strip()

# === 2. Definisikan fitur ===
fitur_kategorikal = ['status tempat tinggal', 'jenis kebutuhan']
fitur_numerikal = ['penghasilan perbulan', 'jumlah tanggungan', 'jumlah kendaraan']
# fitur_ordinal = ['kondisi_barang']
target = 'layak'

# === 3. Mapping kondisi barang (ordinal) ===
# mapping_kondisi = {
#     "agak kurang baik": 1,
#     "baik": 2,
#     "sangat baik": 3,
#     "masih baru": 4
# }
# dataset["kondisi_barang"] = (
#     dataset["kondisi_barang"]
#     .map(mapping_kondisi)
#     .fillna(0)
# )

# Pastikan tidak ada NaN di target
dataset = dataset.dropna(subset=[target])

# === 4. Preprocessing pipeline ===
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), fitur_numerikal),
        ('cat', OneHotEncoder(handle_unknown='ignore'), fitur_kategorikal)
    ]
)

# === 5. Siapkan data ===
X = dataset[fitur_numerikal + fitur_kategorikal]
y = dataset[target]

# === 6. Pipeline model ===
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', KNeighborsClassifier(metric='euclidean', weights='distance'))
])

# === 7. Cross-validation untuk mencari K terbaik ===
k_values = range(1, 20)
cv_scores = []

for k in k_values:
    model.set_params(classifier__n_neighbors=k)
    scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
    cv_scores.append(scores.mean())

# === 8. Ambil hasil terbaik ===
best_k = k_values[np.argmax(cv_scores)]
best_score = max(cv_scores)

# === 9. Visualisasi ===
plt.figure(figsize=(8, 5))
plt.plot(k_values, cv_scores, marker='o', linestyle='-', color='blue')
plt.title('Perbandingan Akurasi terhadap Nilai K (Cross-Validation)')
plt.xlabel('Nilai K')
plt.ylabel('Rata-rata Akurasi')
plt.xticks(k_values)
plt.grid(True)
plt.show()

print(f"Nilai K terbaik: {best_k}")
print(f"Akurasi tertinggi: {best_score:.3f}")
