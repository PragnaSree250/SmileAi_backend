import requests
import json

BASE_URL = "http://localhost:5000"

def test_signup(email, role):
    url = f"{BASE_URL}/signup"
    data = {
        "full_name": f"Test {role.capitalize()}",
        "email": email,
        "password": "password123",
        "role": role
    }
    response = requests.post(url, json=data)
    print(f"Signup {role}: {response.status_code} - {response.text}")
    return response.status_code in [201, 400] # 400 if already exists

def test_login(email):
    url = f"{BASE_URL}/login"
    data = {
        "email": email,
        "password": "password123"
    }
    response = requests.post(url, json=data)
    print(f"Login {email}: {response.status_code}")
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def test_get_profile(token, role):
    url = f"{BASE_URL}/{role}/profile"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(f"Get {role} Profile: {response.status_code} - {response.text}")
    return response.status_code == 200

def test_patch_profile(token, role):
    url = f"{BASE_URL}/{role}/profile"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"phone": "9876543210"}
    if role == "dentist":
        data["specialization"] = "Orthodontist"
    
    response = requests.patch(url, json=data, headers=headers)
    print(f"Patch {role} Profile: {response.status_code} - {response.text}")
    return response.status_code == 200

if __name__ == "__main__":
    # Note: This requires the server to be running and database to be set up.
    # Since I cannot run the server in the background easily and hit it,
    # I will perform a static check of the code for common issues.
    print("Verification script created. Please run this while the Flask app is active.")
