import requests

BASE_URL = "http://127.0.0.1:8000"

def test_flow():
    phone = "1234567890"
    name = "Test User"
    
    print(f"Step 1: Requesting OTP for {phone}...")
    res = requests.post(f"{BASE_URL}/auth/request-otp", json={"phone": phone, "name": name})
    print(res.json())
    
    print("\nStep 2: Verifying OTP (using mock 123456)...")
    res = requests.post(f"{BASE_URL}/auth/verify-otp", json={"phone": phone, "otp": "123456"})
    data = res.json()
    print(data)
    
    if "access_token" in data:
        token = data["access_token"]
        print("\nStep 3: Testing Chat with token...")
        res = requests.post(
            f"{BASE_URL}/chat/", 
            json={"message": "Hello Zura!"},
            headers={"Authorization": f"Bearer {token}"}
        )
        print(res.json())

if __name__ == "__main__":
    print("Ensure the backend is running at http://127.0.0.1:8000 before running this test.")
    try:
        test_flow()
    except Exception as e:
        print(f"Error: {e}")
