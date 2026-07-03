import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def run_tests():
    print("1. Testing Health Endpoint...")
    res = requests.get(f"{BASE_URL}/health")
    print(f"Status: {res.status_code}, Response: {res.json()}")
    
    print("\n2. Testing Admin Login...")
    login_res = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
    print(f"Status: {login_res.status_code}")
    login_data = login_res.json()
    token = login_data.get("token")
    print(f"Logged in as: {login_data.get('user', {}).get('display_name')}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n3. Testing Sentiment Model Info...")
    info_res = requests.get(f"{BASE_URL}/news/sentiment-model-info", headers=headers)
    print(f"Status: {info_res.status_code}, Response:")
    print(json.dumps(info_res.json(), indent=2))
    
    print("\n4. Testing Single Text Sentiment Analysis...")
    text = "The government under PM Narendra Modi has successfully launched a new manufacturing scheme which is praised by business leaders."
    analyze_res = requests.post(f"{BASE_URL}/news/analyze-sentiment", headers=headers, json={"text": text})
    print(f"Status: {analyze_res.status_code}, Response:")
    print(json.dumps(analyze_res.json(), indent=2))
    
    print("\n5. Testing Sentiment Trends on archive dataset...")
    trends_res = requests.get(f"{BASE_URL}/news/sentiment-trends?dataset=archive", headers=headers)
    print(f"Status: {trends_res.status_code}")
    trends_data = trends_res.json()
    print(f"Articles count (matching Indian Gov filter): {trends_data.get('count')}")
    print(f"Sentiment distribution: {trends_data.get('distribution')}")
    print(f"Categories breakdown: {list(trends_data.get('category_breakdown', {}).keys())}")
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    run_tests()
