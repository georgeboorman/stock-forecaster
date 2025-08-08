from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from forecast import load_and_split_data, train_model, forecast_with_model, visualize_forecast

app = FastAPI()

class ForecastRequest(BaseModel):
    days: int

@app.post("/forecast", response_class=HTMLResponse)
def forecast_stock(data: ForecastRequest):
    try:
        # Load and split the data
        train_df, _ = load_and_split_data("stocks.csv")

        # Train the model
        model = train_model(train_df)

        # Forecast using the trained model
        forecast = forecast_with_model(model, data.days)

        # Generate the visualization
        fig = visualize_forecast(train_df, forecast)

        # Return the visualization as HTML
        return fig.to_html(full_html=False, include_plotlyjs="cdn")
    except Exception as e:
        return {"error": str(e)}