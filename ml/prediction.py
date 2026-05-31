import requests
import numpy as np
from sklearn.linear_model import LinearRegression

FIREBASE_URL = "https://smart-resources-kelompok20-default-rtdb.asia-southeast1.firebasedatabase.app"

def ambil_data():
    res_listrik = requests.get(f"{FIREBASE_URL}/listrik.json")
    res_air = requests.get(f"{FIREBASE_URL}/air.json")
    
    listrik = list(res_listrik.json().values()) if res_listrik.json() else []
    air = list(res_air.json().values()) if res_air.json() else []
    
    return listrik, air

def prediksi(data, label, satuan):
    if len(data) < 5:
        print(f"[{label}] Data belum cukup, minimal 5 data.")
        return
    
    nilai = np.array([d['kwh'] if 'kwh' in d else d['liter'] for d in data])
    X = np.arange(len(nilai)).reshape(-1, 1)
    
    model = LinearRegression()
    model.fit(X, nilai)
    
    print(f"\n=== Prediksi 7 Hari ke Depan: {label} ===")
    print(f"Rata-rata saat ini: {round(np.mean(nilai), 3)} {satuan}")
    
    for i in range(1, 8):
        prediksi_nilai = model.predict([[len(nilai) + i]])[0]
        print(f"  Hari ke-{i}: {round(prediksi_nilai, 3)} {satuan}")

if __name__ == "__main__":
    print("Mengambil data dari Firebase...")
    listrik, air = ambil_data()
    prediksi(listrik, "LISTRIK", "kWh")
    prediksi(air, "AIR", "L/min")