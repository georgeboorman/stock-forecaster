import requests
import numpy as np

url = "http://127.0.0.1:8000/forecast"  # Replace with your FastAPI server URL
payload = {"days": 10}  # Specify the number of days to forecast
response = requests.post(url, json=payload)

if response.status_code == 200:
    print("Forecast Result:")
    for entry in response.json():
        print(f"Date: {entry['ds']}, Predicted: {np.round(entry['yhat'],2)}, Upper: {np.round(entry['yhat_upper'],2)}, Lower: {np.round(entry['yhat_lower'],2)}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())