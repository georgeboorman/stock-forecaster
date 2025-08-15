from datetime import datetime
import pickle
from fastapi import FastAPI, Query
from pydantic import BaseModel
from fastapi.responses import HTMLResponse

import os
app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <h1>Stock Forecaster API</h1>
    <p>Use the <code>/forecast</code> endpoint with <b>Ticker</b> and <b>Forecast Date</b> (YYYY-MM-DD) as query parameters.</p>
    <form action="/forecast" method="get">
        <label for="ticker">Ticker:</label>
        <select id="ticker" name="ticker">
            <option value="NVDA">NVDA</option>
            <option value="MSFT">MSFT</option>
            <option value="PLTR">PLTR</option>
        </select><br>
        <label for="forecast_date">Forecast Date (YYYY-MM-DD):</label>
        <input type="text" id="forecast_date" name="forecast_date" value="2025-12-20"><br>
        <input type="submit" value="Generate Forecast">
    </form>
    <p style='color:red; margin-top:20px;'><strong>Disclaimer:</strong> This project and its machine learning model are for educational and informational purposes only and do not constitute financial advice. Do not use these forecasts for investment decisions.</p>
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
    # Select best model file for ticker
    model_files = {
        "NVDA": "models/prophet_NVDA_prod.pkl",
        "MSFT": "models/prophet_MSFT_prod.pkl",
        "PLTR": "models/prophet_PLTR_prod.pkl"
    }
    model_path = model_files.get(ticker)
    if not model_path or not os.path.exists(model_path):
        return {"error": f"No model available for ticker {ticker}"}
    model = pickle.load(open(model_path, "rb"))
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
