
from fastapi import FastAPI, Query
from pydantic import BaseModel
import pickle
from fastapi.responses import HTMLResponse

model = pickle.load(open("prophet_model.pkl", "rb"))
app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <h1>Stock Forecaster API</h1>
    <p>Use the <code>/forecast</code> endpoint with <b>Ticker</b> and <b>Forecast Date</b> (YYYY-MM-DD) as query parameters.</p>
    <form action="/forecast" method="get">
        <label for="ticker">Ticker:</label>
        <input type="text" id="ticker" name="ticker" value="NVDA"><br>
        <label for="forecast_date">Forecast Date (YYYY-MM-DD):</label>
        <input type="text" id="forecast_date" name="forecast_date" value="2025-12-20"><br>
        <input type="submit" value="Generate Forecast">
    </form>
    """

@app.get("/forecast")
def predict_stock(
    ticker: str = Query(..., description="Stock ticker symbol"),
    forecast_date: str = Query(..., description="Forecast date in YYYY-MM-DD format")
):
    """
    Predict stock price for the given ticker and forecast date (YYYY-MM-DD).

    Args:
        ticker (str): Stock ticker symbol.
        forecast_date (str): Date to forecast in YYYY-MM-DD format.

    Returns:
        dict: Predicted stock price for the requested date.
    """
    from datetime import datetime
    try:
        target_date = datetime.strptime(forecast_date, "%Y-%m-%d")
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD."}

    last_train_date = model.history['ds'].max()
    days_ahead = (target_date - last_train_date).days
    if days_ahead < 0:
        return {"error": f"Date must be after the last date in the training data: {last_train_date.strftime('%Y-%m-%d')}"}

    future = model.make_future_dataframe(periods=days_ahead)
    forecast = model.predict(future)
    forecast_row = forecast[forecast['ds'] == target_date]
    if forecast_row.empty:
        return {"error": "Forecast for the requested date is not available."}
    predicted_value = float(forecast_row.iloc[0]["yhat"])
    return {
        "ticker": ticker,
        "date": target_date.strftime('%Y-%m-%d'),
        "predicted_value": predicted_value
    }

@app.get("/")
def read_root():
    return {"message": "Stock forecasting model API."}
