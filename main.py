from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from forecast import load_and_split_data, train_model, forecast_with_model, visualize_forecast
import os
import logging
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)

app = FastAPI()

# Ensure the 'static' directory exists
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class ForecastRequest(BaseModel):
    ticker: str
    days: int

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/favicon.ico")
def favicon():
    return ""

@app.post("/forecast", response_class=HTMLResponse)
def forecast_stock(data: ForecastRequest):
    try:
        # Load and split the data
        train_df, _ = load_and_split_data("stocks.csv", ticker=data.ticker)

        # Train the model
        model = train_model(train_df)

        # Forecast using the trained model
        forecast = forecast_with_model(model, data.days)

        # Generate the visualization
        fig = visualize_forecast(train_df, forecast)

        # Return the visualization wrapped in a div
        return f'<div id="plotly-visualization">{fig.to_html(full_html=False, include_plotlyjs="cdn")}</div>'
    except Exception as e:
        return {"error": str(e)}

@app.get("/forecast_visualization.html")
def get_visualization():
    return FileResponse("forecast_visualization.html")