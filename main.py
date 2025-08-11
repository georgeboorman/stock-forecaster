from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from forecast import load_and_split_data, forecast_with_model
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import pickle
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)

app = FastAPI()

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific frontend URL for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        # Load the trained model from pickle
        with open("prophet_model.pkl", "rb") as f:
            model = pickle.load(f)

        # Forecast using the trained model
        forecast = forecast_with_model(model, data.days)

        # Get the predicted value for the last day in the forecast
        predicted_value = forecast.iloc[-1]["yhat"]
        return {"predicted_value": predicted_value}
    except Exception as e:
        return {"error": str(e)}

## Visualization endpoint removed since we no longer visualize predictions