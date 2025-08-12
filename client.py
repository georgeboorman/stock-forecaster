import json
import requests

data = [["NVDA", 1],
        ["NVDA", 5],
        ["NVDA", 10],
        ["NVDA", 30],
        ["MSFT", 1],
        ["MSFT", 5],
        ["MSFT", 10],
        ["MSFT", 30],
        ["PLTR", 1],
        ["PLTR", 5],
        ["PLTR", 10],
        ["PLTR", 30]]

url = "http://0.0.0.0:8000/forecast"

predictions = []

for record in data:
    ticker, days = record
    payload = {
        "ticker": ticker,
        "days": days
    }
    
    # Convert to JSON string
    payload = json.dumps(payload)
    response = requests.post(url, payload)

    predictions.append(response.json())

# Print all predictions
for prediction in predictions:
    print(f"Ticker: {prediction['ticker']}, Date: {prediction['date']}, Predicted Value: {prediction['predicted_value']}")


data = json.dumps(data)
response = requests.post(url, data)
print(response.json())