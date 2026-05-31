import paho.mqtt.client as mqtt
import json
from datetime import datetime

BROKER = "broker.hivemq.com"
PORT   = 1883
TOPIC_LISTRIK = "smartresources/listrik"
TOPIC_AIR     = "smartresources/air"

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("[OK] Terhubung ke broker MQTT!")
        client.subscribe(TOPIC_LISTRIK)
        client.subscribe(TOPIC_AIR)
        print("Menunggu data dari sensor...\n")
    else:
        print(f"[ERROR] Gagal konek, kode: {rc}")

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    waktu = datetime.now().strftime("%H:%M:%S")
    
    if msg.topic == TOPIC_LISTRIK:
        print(f"[{waktu}] LISTRIK → {data['kwh']} kWh")
    elif msg.topic == TOPIC_AIR:
        print(f"[{waktu}] AIR     → {data['liter']} L/min")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, 
                     client_id="subscriber-kelompok20")
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()