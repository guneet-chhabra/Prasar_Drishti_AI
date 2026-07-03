import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:5000/api"

def make_request(url, method="GET", headers=None, data=None):
    if headers is None:
        headers = {}
    
    req_data = None
    if data is not None:
        req_data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
        
    req = urllib.request.Request(url, method=method, headers=headers, data=req_data)
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err_body = json.loads(e.read().decode("utf-8"))
        except Exception:
            err_body = e.reason
        return e.code, err_body
    except Exception as e:
        return 0, str(e)

def run_tests():
    print("=== Running Prasar Drishti AI Sports API Tests ===")
    
    # 1. Health check
    status, body = make_request(f"{BASE_URL}/health")
    print(f"Health Check: Status {status}, Body: {body}")
    assert status == 200, "Health check failed"
    
    # 2. Login
    login_payload = {
        "username": "admin",
        "password": "admin123"
    }
    status, body = make_request(f"{BASE_URL}/auth/login", method="POST", data=login_payload)
    print(f"Login: Status {status}, Body: {body.get('message') or 'Success'}")
    assert status == 200, "Login failed"
    
    token = body["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Model Info
    status, body = make_request(f"{BASE_URL}/sports/model-info", headers=headers)
    print(f"Sports Model Info: Status {status}, Body: {body}")
    assert status == 200, "Model Info failed"
    
    # 4. Predictions & Simulator
    status, body = make_request(f"{BASE_URL}/sports/predictions", headers=headers)
    print(f"Sports Predictions keys: Status {status}, Keys: {list(body.keys()) if isinstance(body, dict) else body}")
    assert status == 200, "Predictions simulation failed"
    
    # Verify group standings and knockout bracket structure
    if status == 200:
        print("\nVerifying deterministic bracket...")
        bracket = body.get("knockout_bracket", {})
        print("Round of 32 Match count:", len(bracket.get("round_of_32", [])))
        print("Round of 16 Match count:", len(bracket.get("round_of_16", [])))
        print("Quarterfinals Match count:", len(bracket.get("quarterfinals", [])))
        print("Semifinals Match count:", len(bracket.get("semifinals", [])))
        print("Final Match:", bracket.get("final", {}))
        
        # Verify Monte Carlo probabilities exist for a qualified team
        probs = body.get("progression_probabilities", {})
        print("Brazil progression probabilities:", probs.get("Brazil"))
        assert "Brazil" in probs, "Brazil not found in progression probabilities"
        assert "champion" in probs["Brazil"], "Champion probability missing"

    print("\n=== All Tests Passed Successfully ===")

if __name__ == "__main__":
    run_tests()
