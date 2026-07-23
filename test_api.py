import requests

url = "https://worker.brilliance.com/api/v1/lab-grown-diamond-search"

payload = {
    "data": {
        "imgOnly": True,
        "view": "grid",
        "priceMin": 750,
        "priceMax": 100000,
        "caratMin": 1.5,
        "caratMax": 12
    }
}

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

try:
    r = requests.post(url, json=payload, headers=headers, timeout=30)

    print("Status:", r.status_code)
    print("Headers:", r.headers)
    print("Response:")
    print(r.text[:1000])

except Exception as e:
    print(e)