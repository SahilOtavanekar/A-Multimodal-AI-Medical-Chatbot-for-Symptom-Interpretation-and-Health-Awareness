import os
import requests
import time

url = "https://mhuhgozelxwgmtvugxsq.supabase.co/rest/v1/"
print(f"Testing HTTPS connection to {url}")
try:
    start_time = time.time()
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Time: {time.time() - start_time:.2f} seconds")
except requests.exceptions.RequestException as e:
    print(f"Connection failed: {e}")
