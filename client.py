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

url = "http://0.0.0.0:8000/forecast"

predictions = []

for ticker, forecast_date in data:
    response = requests.post(url, json={"ticker": ticker, "forecast_date": forecast_date})
    predictions.append(response.json())

data = json.dumps(data)
# Print all predictions

for prediction in predictions:
    if "error" in prediction:
        print(f"Error for {prediction.get('ticker', 'N/A')}: {prediction['error']}")
    else:
        print(f"Ticker: {prediction['ticker']}, Date: {prediction['date']}, Predicted Value: {prediction['predicted_value']}")