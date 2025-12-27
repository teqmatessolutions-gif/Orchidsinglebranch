import requests
import sys

try:
    response = requests.get("http://localhost:8011/health")
    if response.status_code == 200:
        print("Server is UP")
    else:
        print(f"Server returned status {response.status_code}")
except Exception as e:
    print(f"Server is DOWN: {e}")
