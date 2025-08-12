from fastapi import FastAPI 
import pickle

model = pickle.load(open("prophet_model.pkl", "rb"))

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Stock forecasting model API."}

@app.post("/forecast")
def predict_stock(ticker: str, days: int):
    """
    Predict stock price for the given ticker and number of days.
    
    Args:
        ticker (str): Stock ticker symbol.
        days (int): Number of days to forecast.
    
    Returns:
        dict: Predicted stock price.
    """
    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)
    predicted_row = forecast.iloc[-1]
    predicted_value = float(predicted_row["yhat"])
    predicted_date = str(predicted_row["ds"])[:10]  # YYYY-MM-DD
    return {
        "ticker": ticker,
        "date": predicted_date,
        "predicted_value": predicted_value
    }