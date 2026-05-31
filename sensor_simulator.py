import paho.mqtt.client as mqtt
import json, time, random
from datetime import datetime
import numpy as np

BROKER = "broker.hivemq.com"
PORT   = 1883
TOPIC_LISTRIK = "smartresources/listrik"
TOPIC_AIR     = "smartresources/air"

def get_time_factor():
    """Simulasi pola pemakaian berdasarkan jam."""
    jam = datetime.now().hour
    if 6 <= jam <= 9:   return 1.8   # pagi sibuk
    if 17 <= jam <= 21: return 2.0   # malam sibuk
    if 0 <= jam <= 5:   return 0.3   # tengah malam
    return 1.0

def generate_listrik():
    """Generate data kWh dengan pola realistis."""
    base = 0.5
    factor = get_time_factor()
    noise = np.random.normal(0, 0.05)
    return round(max(0.1, base * factor + noise), 3)

def generate_air():
    """Generate data liter/menit dengan pola realistis."""
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

        client.publish(TOPIC_LISTRIK, json.dumps(data_listrik))
        client.publish(TOPIC_AIR,     json.dumps(data_air))

        print(f"[{ts[:19]}] Listrik: {data_listrik['kwh']} kWh | Air: {data_air['liter']} L/min")
        time.sleep(5)

except KeyboardInterrupt:
    print("\nSensor dihentikan.")
    client.loop_stop()
    client.disconnect()