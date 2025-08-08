from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from prophet import Prophet

app = FastAPI()

class ForecastRequest(BaseModel):
    days: int

@app.post("/forecast")
def forecast_stock(data: ForecastRequest):
    try:
        # Load the data
        df = pd.read_csv("stocks.csv")

        # Prepare the data for Prophet
        df = df.rename(columns={"datetime": "ds", "close": "y"})

        # Split into training and test sets (80/20 split)
        train_size = int(len(df) * 0.8)
        train_df = df[:train_size]

        # Train the Prophet model
        model = Prophet()
        model.fit(train_df)

        # Make future predictions
        future = model.make_future_dataframe(periods=data.days)
        forecast = model.predict(future)

        # Return the forecast
        return forecast.tail(data.days).to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}
    