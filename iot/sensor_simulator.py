import requests
import json, time, random
from datetime import datetime
import numpy as np

FIREBASE_URL = "https://smart-resources-kelompok20-default-rtdb.asia-southeast1.firebasedatabase.app"

def get_time_factor():
    jam = datetime.now().hour
    if 6 <= jam <= 7:   return 2.5
    if 8 <= jam <= 9:   return 1.8
    if 10 <= jam <= 15: return 0.8
    if 16 <= jam <= 17: return 1.5
    if 18 <= jam <= 21: return 2.8
    if 22 <= jam <= 23: return 1.2
    return 0.3

def generate_listrik():
    base = 0.3
    factor = get_time_factor()
    noise = np.random.normal(0, 0.03)
    spike = random.random() < 0.05
    extra = random.uniform(0.5, 1.2) if spike else 0
    return round(max(0.05, base * factor + noise + extra), 3)

def generate_air():
    base = 6.0
    factor = get_time_factor()
    noise = np.random.normal(0, 0.5)
    spike = random.random() < 0.05
    extra = random.uniform(8, 15) if spike else 0
    return round(max(0.1, base * factor + noise + extra), 2)

print("Sensor simulator berjalan. Tekan Ctrl+C untuk berhenti.\n")

try:
    while True:
        ts = datetime.now().isoformat()

        data_listrik = {
            "device_id": "sensor-listrik-01",
            "timestamp": ts,
            "kwh": generate_listrik(),
            "unit": "kWh"
        }

        data_air = {
            "device_id": "sensor-air-01",
            "timestamp": ts,
            "liter": generate_air(),
            "unit": "L/min"
        }

        requests.post(f"{FIREBASE_URL}/listrik.json", json=data_listrik)
        requests.post(f"{FIREBASE_URL}/air.json", json=data_air)

        status_l = "SPIKE!" if data_listrik['kwh'] > 0.8 else "normal"
        status_a = "SPIKE!" if data_air['liter'] > 15 else "normal"

        print(f"[{ts[:19]}] Listrik: {data_listrik['kwh']} kWh [{status_l}] | Air: {data_air['liter']} L/min [{status_a}]")
        time.sleep(5)

except KeyboardInterrupt:
    print("\nSensor dihentikan.")