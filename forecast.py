import pandas as pd
from sklearn.model_selection import train_test_split
from prophet import Prophet

def load_and_split_data(file_path="stocks.csv"):
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
    train_size = int(len(df) * 0.8)
    train_df = df[:train_size]
    test_df = df[train_size:]
    return train_df, test_df

def train_and_forecast(train_df, days):
    """
    Train a Prophet model and forecast the next X days.

    Parameters:
        train_df (DataFrame): Training data.
        days (int): Number of days to forecast.

    Returns:
        DataFrame: Forecasted data.
    """
    model = Prophet()
    model.fit(train_df)
    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)
    return forecast.tail(days)