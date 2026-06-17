import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
import numpy as np
import firebase_admin
from firebase_admin import credentials, db

# ===== FIREBASE CONFIGURATION =====
cred = credentials.Certificate("firebase-service-account.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smart-resources-kelompok20-default-rtdb.asia-southeast1.firebasedatabase.app'
})

# ===== MQTT CONFIGURATION =====
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC_LISTRIK = "smartresources/listrik"
TOPIC_AIR = "smartresources/air"

def get_time_factor():
    jam = datetime.now().hour
    if 6 <= jam <= 9:
        return 1.8
    elif 17 <= jam <= 21:
        return 2.0
    elif 0 <= jam <= 5:
        return 0.3
    return 1.0

def generate_listrik():
    base = 0.5
    factor = get_time_factor()
    noise = np.random.normal(0, 0.05)
    return round(max(0.1, base * factor + noise), 3)

def generate_air():
    base = 8.0
    factor = get_time_factor()
    noise = np.random.normal(0, 0.5)
    return round(max(0.5, base * factor + noise), 2)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[OK] Terhubung ke broker MQTT!")
    else:
        print(f"[ERROR] Gagal konek, kode: {rc}")

client = mqtt.Client(client_id="sensor-kelompok20")
client.on_connect = on_connect
client.connect(BROKER, PORT, 60)
client.loop_start()

print("=== Sensor Simulator - Kelompok 20 ===")
print("Sending data to MQTT AND Firebase...")
print("Press Ctrl+C to stop\n")

try:
    while True:
        ts = datetime.now().isoformat()
        server_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
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

        # Publish to MQTT
        client.publish(TOPIC_LISTRIK, json.dumps(data_listrik))
        client.publish(TOPIC_AIR, json.dumps(data_air))

        # Save to Firebase
        db.reference('listrik').push(data_listrik)
        db.reference('air').push(data_air)

        print(f"[{server_time}] Listrik: {data_listrik['kwh']} kWh | Air: {data_air['liter']} L/min → Saved to Firebase!")

        time.sleep(5)
        
except KeyboardInterrupt:
    print("\nSimulator stopped.")
    client.loop_stop()
    client.disconnect()