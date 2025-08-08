import requests

url = "http://127.0.0.1:8000/forecast"  # Replace with your FastAPI server URL
payload = {"days": 10}  # Specify the number of days to forecast
response = requests.post(url, json=payload)

if response.status_code == 200:
    print("Forecast Result:")
    print(response.json())
else:
    print(f"Error: {response.status_code}")
    print(response.json())