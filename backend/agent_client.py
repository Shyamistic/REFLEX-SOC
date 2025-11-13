import requests
import socket
import platform
import time
import uuid
import random

BACKEND_URL = "http://localhost:8899"
ORG_ID = "default_org"  # ADD THIS - Multi-tenant org

AGENT_ID = str(uuid.uuid4())
HOSTNAME = socket.gethostname()

EVENT_TYPES = ["process_start", "file_write", "network_connection"]

def register():
    info = {
        "agent_id": AGENT_ID,
        "hostname": HOSTNAME,
        "ip": requests.get("https://api.ipify.org").text,
        "os": platform.system(),
        "version": "1.0",
        "org_id": ORG_ID  # ADD THIS
    }
    res = requests.post(f"{BACKEND_URL}/agent/register", json=info)
    print(res.json())

def heartbeat():
    res = requests.post(f"{BACKEND_URL}/agent/heartbeat", json={
        "agent_id": AGENT_ID,
        "org_id": ORG_ID  # ADD THIS
    })
    print(f"Heartbeat: {res.status_code}")

def generate_event():
    evt = {
        "agent_id": AGENT_ID,
        "event_type": random.choice(EVENT_TYPES),
        "timestamp": int(time.time()),
        "details": {
            "process": random.choice(["python", "curl", "bash", "vim"]),
            "file": random.choice(["/tmp/config", "/home/ops/secret.txt", ""]),
            "ip": random.choice(["1.2.3.4", "8.8.8.8", "192.168.1.5"])
        },
        "org_id": ORG_ID  # ADD THIS
    }
    return evt

def send_event(event):
    try:
        res = requests.post(f"{BACKEND_URL}/agent/event", json=event)
        print("Event sent:", res.status_code)
    except Exception as e:
        print("Event send failed:", e)

if __name__ == "__main__":
    register()
    while True:
        heartbeat()
        if random.random() < 0.5:
            evt = generate_event()
            send_event(evt)
        time.sleep(30)
