import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test():
    # Login
    login_res = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
    token = login_res.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get trends on today
    res = requests.get(f"{BASE_URL}/news/sentiment-trends?dataset=today", headers=headers)
    print(f"Status: {res.status_code}")
    data = res.json()
    print(f"Filtered Articles Count: {data.get('count')}")
    print(f"Sentiment Distribution: {data.get('distribution')}")
    
    print("\n--- Listing Filtered Articles and Sentiments ---")
    for art in data.get("articles", []):
        print(f"Title: {art.get('title')}")
        print(f"  Category: {art.get('category')}")
        print(f"  Sentiment: {art.get('sentiment_name')} ({art.get('sentiment_confidence'):.2f})")
        print()

if __name__ == "__main__":
    test()
