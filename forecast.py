import pandas as pd
from sklearn.model_selection import train_test_split
from prophet import Prophet
import plotly.graph_objects as go
import logging
import numpy as np

logging.getLogger("cmdstanpy").setLevel(logging.WARNING)

def load_and_split_data(file_path="stocks.csv", ticker="NVDA"):
    """
    Load data from CSV and split into training and test sets.

    Parameters:
        file_path (str): Path to the CSV file.

    Returns:
        tuple: Training and test DataFrames.
    """
    df = pd.read_csv(file_path, parse_dates=["date"])
    df = df.rename(columns={"date": "ds", "close": "y"})
    df.dropna(inplace=True)
    df = df[df['ticker'] == ticker]
    train_size = int(len(df) * 0.95)
    train_df = df[:train_size]
    test_df = df[train_size:]
    return train_df, test_df

def train_model(train_df):
    """
    Train a Prophet model.

    Parameters:
        train_df (DataFrame): Training data.

    Returns:
        Prophet: Trained Prophet model.
    """
    model = Prophet(changepoint_prior_scale=0.2)
    model.fit(train_df)
    return model

def forecast_with_model(model, days):
    """
    Use a trained Prophet model to forecast the next X days.

    Parameters:
        model (Prophet): Trained Prophet model.
        days (int): Number of days to forecast.

    Returns:
        DataFrame: Forecasted data for the requested days.
    """
    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)
    return forecast.tail(days)

## Visualization function removed. Only prediction values are now returned by the API.

if __name__ == "__main__":
    try:
        # Load and split the data
        train_df, test_df = load_and_split_data("stocks.csv")

        # Train the model
        model = train_model(train_df)

        # Forecast using the trained model
        forecast = forecast_with_model(model, days=30)  # Example: forecast for 30 days

        # Visualize the forecast (removed)
    except Exception as e:
        print(f"An error occurred: {e}")