import pandas as pd
from sklearn.model_selection import train_test_split
from prophet import Prophet
import mlflow
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
        DataFrame: Forecasted data.
    """
    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)
    return forecast.tail(days)

def log_to_mlflow(model, forecast, train_df):
    """
    Log the model and forecast results to MLflow.

    Parameters:
        model (Prophet): Trained Prophet model.
        forecast (DataFrame): Forecasted data.
        train_df (DataFrame): Training data.
    """
    with mlflow.start_run() as run:
        # Log model
        mlflow.prophet.log_model(model, "model")

        # Log forecast data directly as an artifact
        forecast_buffer = forecast.to_csv(index=False)
        mlflow.log_text(forecast_buffer, f"forecast_{run.info.run_id}.csv")

        # Log training data directly as an artifact
        train_buffer = train_df.to_csv(index=False)
        mlflow.log_text(train_buffer, f"train_data_{run.info.run_id}.csv")

        # Log parameters
        mlflow.log_param("training_data_size", len(train_df))
        mlflow.log_param("forecast_periods", len(forecast))

def visualize_forecast(train_df, forecast):
    """
    Create a visualization of the training data and forecasted values, including upper and lower bounds.

    Parameters:
        train_df (DataFrame): Training data.
        forecast (DataFrame): Forecasted data.

    Returns:
        None
    """
    fig = go.Figure()

    # Add training data
    fig.add_trace(go.Scatter(x=np.array(train_df["ds"]), y=train_df["y"], mode="lines", name="Training Data"))

    # Add forecasted data
    fig.add_trace(go.Scatter(x=np.array(forecast["ds"]), y=forecast["yhat"], mode="lines", name="Forecast"))

    # Add upper bound
    fig.add_trace(go.Scatter(x=np.array(forecast["ds"]), y=forecast["yhat_upper"], mode="lines", name="Upper Bound", line=dict(dash="dot")))

    # Add lower bound
    fig.add_trace(go.Scatter(x=np.array(forecast["ds"]), y=forecast["yhat_lower"], mode="lines", name="Lower Bound", line=dict(dash="dot")))

    # Customize layout
    fig.update_layout(title="Training Data and Forecast with Confidence Intervals", xaxis_title="Date", yaxis_title="Value")

    # Show plot
    fig.show()

if __name__ == "__main__":
    try:
        # Load and split the data
        train_df, test_df = load_and_split_data("stocks.csv")

        # Train the model
        model = train_model(train_df)

        # Forecast using the trained model
        forecast = forecast_with_model(model, days=30)  # Example: forecast for 30 days

        # Log to MLflow
        log_to_mlflow(model, forecast, train_df)

        # Visualize the forecast
        visualize_forecast(train_df, forecast)
    except Exception as e:
        print(f"An error occurred: {e}")