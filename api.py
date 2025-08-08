from fastapi import FastAPI
from pydantic import BaseModel
from forecast import load_and_split_data, train_model, forecast_with_model, visualize_forecast

app = FastAPI()

class ForecastRequest(BaseModel):
    days: int

@app.post("/forecast")
def forecast_stock(data: ForecastRequest):
    try:
        # Load and split the data
        train_df, _ = load_and_split_data("stocks.csv")

        # Train the model
        model = train_model(train_df)

        # Forecast using the trained model
        forecast = forecast_with_model(model, data.days)

        # Visualize the forecast
        visualize_forecast(train_df, forecast)

        # return {"message": "Visualization generated successfully."}
    except Exception as e:
        return {"error": str(e)}