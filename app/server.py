
from fastapi import FastAPI
from pydantic import BaseModel
import pickle

model = pickle.load(open("prophet_model.pkl", "rb"))

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Stock forecasting model API."}


class ForecastRequest(BaseModel):
    ticker: str
    forecast_date: str  # MM/DD/YYYY


@app.post("/forecast")
def predict_stock(request: ForecastRequest):
    """
    Predict stock price for the given ticker and forecast date (MM/DD/YYYY).

    Args:
        ticker (str): Stock ticker symbol.
        forecast_date (str): Date to forecast in MM/DD/YYYY format.

    Returns:
        dict: Predicted stock price for the requested date.
    """
    from datetime import datetime, timedelta
    # Parse the requested date
    try:
        target_date = datetime.strptime(request.forecast_date, "%m/%d/%Y")
    except ValueError:
        return {"error": "Invalid date format. Use MM/DD/YYYY."}

    # Find the last date in the model's training data
    last_train_date = model.history['ds'].max()
    days_ahead = (target_date - last_train_date).days
    if days_ahead < 0:
        return {"error": "Date must be after the last date in the training data: {}".format(last_train_date.strftime('%Y-%m-%d'))}

    # Generate future dataframe up to the requested date
    future = model.make_future_dataframe(periods=days_ahead)
    forecast = model.predict(future)
    # Find the row for the requested date
    forecast_row = forecast[forecast['ds'] == target_date]
    if forecast_row.empty:
        return {"error": "Forecast for the requested date is not available."}
    predicted_value = float(forecast_row.iloc[0]["yhat"])
    return {
        "ticker": request.ticker,
        "date": target_date.strftime('%Y-%m-%d'),
        "predicted_value": predicted_value
    }