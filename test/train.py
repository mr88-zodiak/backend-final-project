import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score,confusion_matrix, classification_report,ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import joblib

# === 1. Baca dan normalisasi huruf ===
dataset = pd.read_excel('./data_bersih_sinkron.xlsx')
dataset = dataset.drop('kondisi_barang', axis=1)
for col in dataset.select_dtypes(include='object').columns:
    dataset[col] = dataset[col].str.lower().str.strip()

# === 2. Definisikan fitur ===
fitur_kategorikal = ['status tempat tinggal', 'jenis kebutuhan']
fitur_numerikal = ['penghasilan perbulan', 'jumlah tanggungan', 'jumlah kendaraan']
# fitur_ordinal = ['kondisi_barang']
label = 'layak'

# === 3. Mapping kondisi barang ===
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

# === 4. Preprocessing & Pipeline ===
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), fitur_numerikal),
        ('cat', OneHotEncoder(handle_unknown='ignore'), fitur_kategorikal)
    ]
)

model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', KNeighborsClassifier(n_neighbors=6, metric='euclidean', weights='uniform'))
]) 

label_encoder = LabelEncoder()
dataset[label] = label_encoder.fit_transform(dataset[label])

X = dataset[fitur_numerikal + fitur_kategorikal ]
y = dataset[label]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# === 6. Latih dan evaluasi ===
model.fit(X_train, y_train)
accuracy = model.score(X_test, y_test)
# print(f"Akurasi model: {accuracy*100:.2f}%")

# === 7. Prediksi data baru ===
# new_data = pd.DataFrame({
#     'penghasilan perbulan': [2500000],
#     'jumlah tanggungan': [2],
#     'jumlah kendaraan': [1],
#     'status tempat tinggal': ['milik sendiri'],
#     'jenis kebutuhan': ['baju bekas'],
# })
# prediction = model.predict(new_data)
# print(int(prediction[0]))
# joblib.dump(model, 'knn_model_fix.pkl')
# print(f"{'Layak' if prediction[0] == 'iya' or prediction[0] == 1 else 'Tidak Layak'}")

# y_pred = model.predict(X_test)
# print("Confusion Matrix:")
# print(confusion_matrix(y_test, y_pred))

# print("Classification Report:")
# print(classification_report(y_test, y_pred))
# cm = confusion_matrix(y_test, y_pred)
# disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=model.classes_)

# plt.figure(figsize=(6, 5))
# disp.plot(cmap='Blues', values_format='d')
# plt.title("Confusion Matrix - KNN (k terbaik)")
# plt.show()

# train_acc = model.score(X_train, y_train)
# test_acc = model.score(X_test, y_test)

# print(f"Akurasi Training: {train_acc*100:.2f}%")
# print(f"Akurasi Testing: {test_acc*100:.2f}%")
