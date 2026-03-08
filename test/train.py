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
dataset = pd.read_excel('test/dataset/data.xlsx')
dataset['layak'] = dataset['layak'].map({
    'iya': 1,
    'tidak': 0
})

print(dataset['layak'].unique())
# print(dataset.classes_)

# dataset = dataset.drop('kondisi_barang', axis=1)
for col in dataset.select_dtypes(include='object').columns:
    dataset[col] = dataset[col].str.lower().str.strip()

# === 2. Definisikan fitur ===
fitur_kategorikal = ['status tempat tinggal']
fitur_numerikal = ['penghasilan perbulan', 'jumlah tanggungan', 'jumlah kendaraan']
label = 'layak'


# === 4. Preprocessing & Pipeline ===
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), fitur_numerikal),
        ('cat', OneHotEncoder(handle_unknown='ignore'), fitur_kategorikal)
    ]
)

model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', KNeighborsClassifier(n_neighbors=12, metric='euclidean', weights='distance'))
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
new_data = pd.DataFrame({
    'penghasilan perbulan': [2500000],
    'jumlah tanggungan': [2],
    'jumlah kendaraan': [1],
    'status tempat tinggal': ['milik sendiri'],
})
prediction = model.predict(new_data)
print(int(prediction[0]))

# === 8. Transform data baru (WAJIB) ===
X_new_transformed = model.named_steps['preprocessor'].transform(new_data)

# === 9. Ambil jarak & tetangga terdekat ===
distances, indices = model.named_steps['classifier'].kneighbors(X_new_transformed)

print("\nPrediksi:", int(prediction[0]))
print("\nJarak ke tetangga terdekat:")

for i in range(len(distances[0])):
    idx = indices[0][i]
    print(
        f"Tetangga {i+1} | "
        f"Index data latih: {idx} | "
        f"Label: {y_train.iloc[idx]} | "
        f"Jarak: {distances[0][i]:.4f}"
    )

# joblib.dump(model, 'knn_model_fix.pkl')
print(f"{'Layak' if prediction[0] == 1 else 'Tidak Layak'}")

y_pred = model.predict(X_test)
# print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("Classification Report:")
print(classification_report(y_test, y_pred))
labels = ['Tidak Layak', 'Layak']
cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)

plt.figure(figsize=(6, 5))
disp.plot(cmap='Blues', values_format='d')
plt.title("Confusion Matrix - KNN")
plt.show()

train_acc = model.score(X_train, y_train)
test_acc = model.score(X_test, y_test)

print(f"Akurasi Training: {train_acc*100:.2f}%")
print(f"Akurasi Testing: {test_acc*100:.2f}%")
