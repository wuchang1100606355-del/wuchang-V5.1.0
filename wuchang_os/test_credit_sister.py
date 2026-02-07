import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_credit_flow():
    print("--- 1. Testing Credit Sister Logic via API ---")
    
    # Simulate User asking for balance
    payload = {"message": "我的抵免額有多少？"}
    try:
        res = requests.post(f"{BASE_URL}/api/chat", json=payload)
        print(f"User Query: {payload['message']}")
        print(f"Response: {res.json()['reply'][:100]}...") 
    except Exception as e:
        print(f"Query Failed: {e}")

    # Simulate God Mode Granting Credits (Brother Action)
    print("\n--- 2. Testing God Mode Granting Credits ---")
    grant_cmd = {
        "tool_use": True,
        "action": "manage_credit",
        "params": {
            "operation": "add",
            "user_id": "Brother_Juers",
            "amount": 500,
            "description": "Initial Grant for Testing"
        }
    }
    
    # We need to simulate being Core VIP to use this.
    # First, authenticate as VIP
    auth_payload = {"message": "97573469"} # VIP Code
    requests.post(f"{BASE_URL}/api/chat", json=auth_payload)
    
    # Now send the command wrapped in natural language (or just trigger it if logic allows)
    # Since our server parses JSON blocks from LLM response, we need to simulate the LLM *generating* the tool use.
    # However, the user *inputs* the command in natural language, and the LLM *outputs* the JSON.
    # To test the *execution* logic directly without relying on LLM generation (which we can't control easily here),
    # we can verify if the endpoint handles it?
    # Actually, the server executes JSON found in the *LLM's reply*.
    # So we can't easily test "God Mode execution" via the chat endpoint unless we mock the LLM or have the LLM actually output it.
    
    # ALTERNATIVE: Use the direct python interface to verify logic first.
    from credit_sister_core import credit_sister
    
    print("Direct Logic Test:")
    # 1. Check Initial Balance
    bal = credit_sister.get_balance("Brother_Juers")
    print(f"Initial Balance: {bal}")
    
    # 2. Add Credits
    tx = credit_sister.transaction("Brother_Juers", 100, "test_grant", "Testing Script")
    print(f"Transaction Result: {tx}")
    
    # 3. Check New Balance
    new_bal = credit_sister.get_balance("Brother_Juers")
    print(f"New Balance: {new_bal}")
    
    assert new_bal == bal + 100
    print("Logic Verification Passed!")

if __name__ == "__main__":
    test_credit_flow()
