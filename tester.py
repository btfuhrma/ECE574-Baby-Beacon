import requests
import time
import random

# Django server URLs
BASE_URL = "http://127.0.0.1:8000"  # replace with your server IP/domain
GET_TOKEN_URL = f"{BASE_URL}/api/getToken/"
SENSOR_DATA_URL = f"{BASE_URL}/api/data/"

# Stored API key (simulating ESP32 memory)
api_key = None

def get_api_key():
    """
    Poll the Django endpoint to get the current active API key
    """
    global api_key
    try:
        response = requests.get(GET_TOKEN_URL)
        response.raise_for_status()
        data = response.json()
        if data.get("api_key"):
            api_key = data["api_key"]
            print(f"[INFO] Got API key: {api_key}")
        else:
            print("[INFO] No active API key yet.")
    except requests.RequestException as e:
        print(f"[ERROR] Failed to get API key: {e}")

def send_sensor_data():
    """
    Send simulated temperature and amplitude data to Django
    """
    if not api_key:
        print("[WARN] No API key, cannot send data.")
        return

    temperature = round(random.uniform(25.0, 30.0), 2)  # simulated °C
    amplitude = round(random.uniform(50.0, 80.0), 2)   # simulated sound amplitude

    payload = {
        "api_key": api_key,
        "temperature": temperature,
        "amplitude": amplitude
    }

    try:
        response = requests.post(SENSOR_DATA_URL, json=payload)
        if response.status_code == 200:
            print(f"[SUCCESS] Data sent: {payload}")
        else:
            print(f"[ERROR] Server response: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        print(f"[ERROR] Failed to send data: {e}")

def main():
    """
    Simulate the ESP32 main loop:
    - Check for token if missing
    - Send sensor data
    """
    while True:
        if not api_key:
            get_api_key()
        send_sensor_data()
        time.sleep(5)  # wait 10 seconds before next loop

if __name__ == "__main__":
    main()
