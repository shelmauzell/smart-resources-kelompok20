import json
import requests
import numpy as np
from sklearn.ensemble import IsolationForest

FIREBASE_URL = "https://smart-resources-kelompok20-default-rtdb.asia-southeast1.firebasedatabase.app"

def ambil_data():
    res_listrik = requests.get(f"{FIREBASE_URL}/listrik.json")
    res_air = requests.get(f"{FIREBASE_URL}/air.json")
    
    listrik = list(res_listrik.json().values()) if res_listrik.json() else []
    air = list(res_air.json().values()) if res_air.json() else []
    
    return listrik, air

def deteksi_anomali(data, label):
    if len(data) < 10:
        print(f"[{label}] Data belum cukup, minimal 10 data.")
        return
    
    nilai = np.array([d['kwh'] if 'kwh' in d else d['liter'] for d in data]).reshape(-1, 1)
    
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(nilai)
    hasil = model.predict(nilai)
    
    anomali = [data[i] for i, h in enumerate(hasil) if h == -1]
    
    print(f"\n=== Anomaly Detection: {label} ===")
    print(f"Total data: {len(data)}")
    print(f"Anomali ditemukan: {len(anomali)}")
    
    if anomali:
        print("Data anomali:")
        for a in anomali:
            nilai_a = a.get('kwh', a.get('liter'))
            print(f"  - {a['timestamp'][:19]} → {nilai_a}")
    else:
        print("Tidak ada anomali ditemukan.")

if __name__ == "__main__":
    print("Mengambil data dari Firebase...")
    listrik, air = ambil_data()
    deteksi_anomali(listrik, "LISTRIK")
    deteksi_anomali(air, "AIR")