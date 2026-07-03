import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000/api"

def trigger():
    print("Logging in as admin...")
    login_res = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
    token = login_res.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Triggering background historical scrape (last-month)...")
    res = requests.post(f"{BASE_URL}/news/scrape-last-month", headers=headers)
    print(f"Status: {res.status_code}")
    print("Response:")
    print(json.dumps(res.json(), indent=2))

if __name__ == "__main__":
    trigger()
