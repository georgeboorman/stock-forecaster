import requests
import logging
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)

url = "http://127.0.0.1:8000/forecast"  # Replace with your FastAPI server URL
payload = {"days": 30}  # Specify the number of days to forecast
response = requests.post(url, json=payload)

if response.status_code == 200:
    pass 
    # The visualization is generated and displayed in the browser by api.py, so we use pass here.
    # print("Visualization generated successfully.")
else:
    print(f"Error: {response.status_code}")
    print(response.json())