import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def trigger():
    print("Logging in as admin...")
    login_res = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
    token = login_res.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Triggering scrape for today's articles...")
    payload = {
        "categories": ["sports", "national", "international", "business", "miscellaneous"],
        "limit": 10,
        "days": 1,
        "pages": 3,
        "dataset": "today",
        "government_only": False
    }
    
    scrape_res = requests.post(f"{BASE_URL}/news/scrape", headers=headers, json=payload)
    print(f"Status: {scrape_res.status_code}")
    print("Response:")
    print(json.dumps(scrape_res.json(), indent=2))

if __name__ == "__main__":
    trigger()
