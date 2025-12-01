import requests
import json

BASE_URL = "http://127.0.0.1:8011/api"
LOGIN_URL = f"{BASE_URL}/auth/login"

def verify_e2e():
    session = requests.Session()
    
    # 1. Login
    print("1. Logging in...")
    try:
        login_payload = {
            "username": "admin@example.com",
            "password": "password"
        }
        # Try JSON login first
        response = session.post(LOGIN_URL, json=login_payload)
        if response.status_code != 200:
            # Try form data
            response = session.post(LOGIN_URL, data=login_payload)
            
        if response.status_code != 200:
            print(f"✗ Login failed: {response.status_code} {response.text}")
            return
            
        token = response.json().get("access_token")
        if not token:
            print("✗ No access token returned")
            return
            
        session.headers.update({"Authorization": f"Bearer {token}"})
        print("✓ Login successful")
        
    except Exception as e:
        print(f"✗ Login exception: {e}")
        return

    # 2. Verify Service Requests Serialization (The 500 error fix)
    print("\n2. Verifying Service Requests Serialization...")
    try:
        response = session.get(f"{BASE_URL}/service-requests?include_checkout_requests=true")
        if response.status_code == 200:
            print(f"✓ Fetch successful. Count: {len(response.json())}")
        else:
            print(f"✗ Fetch failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"✗ Fetch exception: {e}")

    # 3. Verify Assigned Service Status Update
    print("\n3. Verifying Assigned Service Status Update...")
    try:
        response = session.get(f"{BASE_URL}/services/assigned")
        if response.status_code != 200:
            print(f"✗ Failed to get assigned services: {response.status_code}")
            return
            
        services = response.json()
        if not services:
            print("⚠ No assigned services found to update.")
        else:
            target = services[0]
            target_id = target['id']
            current_status = target['status']
            print(f"Target Service ID: {target_id}, Status: {current_status}")
            
            new_status = "in_progress" if current_status == "pending" else "completed"
            if current_status == "completed":
                new_status = "pending"
                
            print(f"Updating to: {new_status}")
            response = session.patch(f"{BASE_URL}/services/assigned/{target_id}", json={"status": new_status})
            
            if response.status_code == 200:
                print(f"✓ Update successful. New Status: {response.json()['status']}")
            else:
                print(f"✗ Update failed: {response.status_code} {response.text}")
                
    except Exception as e:
        print(f"✗ Update exception: {e}")

if __name__ == "__main__":
    verify_e2e()
