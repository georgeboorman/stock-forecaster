import json
import requests


from datetime import datetime, timedelta

# Example: forecast for 1, 5, 10, 30 days ahead from today for each ticker
tickers = ["NVDA", "MSFT", "PLTR"]
days_list = [1, 5, 10, 30]
today = datetime.today()
data = []
for ticker in tickers:
    for days in days_list:
        forecast_date = (today + timedelta(days=days)).strftime("%m/%d/%Y")
        data.append([ticker, forecast_date])

predictions = []
data = json.dumps(data)
url = "http://0.0.0.0:8000/forecast"

predictions_post = []
predictions_get = []

for ticker, forecast_date in data:
    # POST request (JSON)
    response_post = requests.post(url, json={"ticker": ticker, "forecast_date": forecast_date})
    predictions_post.append(response_post.json())

    # GET request (query params)
    params = {"ticker": ticker, "forecast_date": forecast_date}
    response_get = requests.get(url, params=params)
    try:
        predictions_get.append(response_get.json())
    except Exception:
        predictions_get.append({"error": f"Non-JSON response: {response_get.text}"})

# Print all POST predictions
print("POST request predictions:")
for prediction in predictions_post:
    if "error" in prediction:
        print(f"Error for {prediction.get('ticker', 'N/A')}: {prediction['error']}")
    else:
        print(f"Ticker: {prediction['ticker']}, Date: {prediction['date']}, Predicted Value: {prediction['predicted_value']}")

# Print all GET predictions
print("\nGET request predictions:")
for prediction in predictions_get:
    if "error" in prediction:
        print(f"Error for {prediction.get('ticker', 'N/A')}: {prediction['error']}")
    else:
        print(f"Ticker: {prediction['ticker']}, Date: {prediction['date']}, Predicted Value: {prediction['predicted_value']}")