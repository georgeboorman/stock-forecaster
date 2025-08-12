import requests
from datetime import datetime, timedelta
today = datetime.today()
predictions = []
predictions_post = []
predictions_get = []
# Example: forecast for 1, 5, 10, 30 days ahead from today for each ticker
tickers = ["NVDA", "MSFT", "PLTR"]
days_list = [1, 5, 10, 30]
today = datetime.today()
data = []
for ticker in tickers:
    for days in days_list:
        forecast_date = (today + timedelta(days=days)).strftime("%Y-%m-%d")
        data.append((ticker, forecast_date))

url = "http://0.0.0.0:8000/forecast"
predictions = []

for ticker, forecast_date in data:
    params = {"ticker": ticker, "forecast_date": forecast_date}
    response = requests.get(url, params=params)
    try:
        predictions.append(response.json())
    except Exception:
        predictions.append({"error": f"Non-JSON response: {response.text}"})

print("GET request predictions:")
for prediction in predictions:
    if "error" in prediction:
        print(f"Error for {prediction.get('ticker', 'N/A')}: {prediction['error']}")
    else:
        print(f"Ticker: {prediction['ticker']}, Date: {prediction['date']}, Predicted Value: {prediction['predicted_value']}")