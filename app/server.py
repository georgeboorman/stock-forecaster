
from fastapi import FastAPI, Query
from pydantic import BaseModel
import pickle

model = pickle.load(open("prophet_model.pkl", "rb"))

app = FastAPI()

# class ForecastRequest(BaseModel):
#     ticker: str
#     forecast_date: str  # MM/DD/YYYY


@app.get("/")
def read_root():
    return {"message": "Stock forecasting model API. Visit /docs for API documentation, or use the /forecast endpoint to get predictions.\n"
    "Example request: /forecast?ticker=NVDA&forecast_date=2025-12-20"}

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
