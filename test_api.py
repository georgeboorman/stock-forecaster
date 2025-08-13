import requests
import logging
import webbrowser
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)

url = "http://127.0.0.1:8000/forecast"  
payload = {"ticker": "NVDA", "forecast_date": "12/31/2025"} 
response = requests.post(url, json=payload)

if response.status_code == 200:
    # Print the predicted value
    print("Predicted value:", response.json().get("predicted_value"))
else:
    print(f"Error: {response.status_code}")
    print(response.json())