import os
import urllib.request

url = os.getenv("API_URL", "http://127.0.0.1:5000") + "/api/health"
with urllib.request.urlopen(url, timeout=10) as response:
    body = response.read().decode()
    print(response.status, body)
    if response.status != 200:
        raise SystemExit(1)
