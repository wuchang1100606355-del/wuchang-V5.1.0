import hashlib
import datetime

# 🔐 SECURITY KEY - MUST MATCH THE ENGINE
SECRET_KEY = "WUCHANG_SPACETIME_RULE_CORE_SECRET_V1"

def get_daily_token():
    """Generates the 8-character daily access token based on the secret key and current date."""
    today = datetime.datetime.now().strftime("%Y%m%d")
    raw = f"{SECRET_KEY}{today}"
    # Use SHA256 and take first 8 characters
    token = hashlib.sha256(raw.encode()).hexdigest()[:8].upper()
    return token

if __name__ == "__main__":
    print("--------------------------------------------------")
    print("   🔑 SPATIOTEMPORAL ACCESS TOKEN GENERATOR")
    print("--------------------------------------------------")
    token = get_daily_token()
    print(f"\n   📅 DATE: {datetime.datetime.now().strftime('%Y-%m-%d')}")
    print(f"   ��️  TOKEN: {token}")
    print("\n--------------------------------------------------")
    print("Provide this token to authorized users for today's access.")
    input("\nPress Enter to exit...")
