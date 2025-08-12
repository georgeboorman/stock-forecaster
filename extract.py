import os
import requests
import pandas as pd
from datetime import date
def read_api_key(filepath='secrets.txt', key_name='TWELVE_DATA_API_KEY'):
    """
    Reads the API key from the secrets file.
    """
    with open(filepath, 'r') as file:
        for line in file:
            if line.strip().startswith(key_name + '='):
                return line.strip().split('=', 1)[1]
    raise ValueError(f"{key_name} not found in {filepath}")

def get_stock_data(tickers, api_key, interval='1day'):
    """
    Fetch only missing daily stock data from Twelve Data API and return as a dict of DataFrames.

    Parameters:
        tickers (list): List of stock symbols (e.g., ['NVDA', 'PLTR'])
        api_key (str): Your Twelve Data API key
        interval (str): Data interval (e.g., '1day')

    Returns:
        dict: Dictionary of DataFrames keyed by ticker symbol
    """
    base_url = "https://api.twelvedata.com/time_series"
    result = {}
    today = pd.Timestamp.today().normalize()
    # Load existing CSV if it exists
    try:
        existing_df = pd.read_csv("stocks.csv", parse_dates=["date"])
    except FileNotFoundError:
        existing_df = pd.DataFrame()

    for ticker in tickers:
        # Find last date for this ticker in CSV
        if not existing_df.empty and ticker in existing_df["ticker"].values:
            ticker_df = existing_df[existing_df["ticker"] == ticker]
            last_date = ticker_df["date"].max()
            last_date = pd.to_datetime(last_date).normalize()
        else:
            last_date = None

        # If up to date, skip
        if last_date is not None and last_date >= today:
            print(f"{ticker} is already up to date (last date: {last_date.date()})")
            result[ticker] = None
            continue

        # Calculate how many days to fetch
        if last_date is not None:
            start_date = last_date + pd.Timedelta(days=1)
        else:
            # If no data, fetch up to 120 days
            start_date = today - pd.Timedelta(days=120)
        days_to_fetch = (today - start_date).days + 1
        if days_to_fetch <= 0:
            print(f"No new data needed for {ticker}")
            result[ticker] = None
            continue

        params = {
            'symbol': ticker,
            'interval': interval,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': today.strftime('%Y-%m-%d'),
            'apikey': api_key
        }
        response = requests.get(base_url, params=params)
        data = response.json()
        if "values" in data:
            df = pd.DataFrame(data['values'])
            df['ticker'] = ticker
            df['date'] = pd.to_datetime(df['datetime'])
            # Convert columns to float
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            # Keep only the required columns in the correct order
            df = df[['date', 'open', 'high', 'low', 'close', 'volume', 'ticker']]
            result[ticker] = df
        else:
            print(f"Error fetching data for {ticker}: {data.get('message', 'Unknown error')}")
            result[ticker] = None

    return result


def save_to_csv(data_dict, filename="stocks.csv"):
    """
    Append all stock data to a CSV file. If the file does not exist, it will be created with headers.

    Parameters:
        data_dict (dict): Dictionary of DataFrames keyed by ticker symbol
        filename (str): Name of the CSV file to save data
    """
    combined_df = pd.concat(data_dict.values(), ignore_index=True)
    write_header = not os.path.exists(filename)
    combined_df.to_csv(filename, mode='a', header=write_header, index=False)
    print(f"Data appended to {filename}")

if __name__ == "__main__":
    try:
        api_key = read_api_key()
        tickers = ['NVDA', 'PLTR', 'MSFT']
        stock_data = get_stock_data(tickers, api_key)
        save_to_csv(stock_data)
        for ticker, df in stock_data.items():
            if df is not None:
                print(f"Data for {ticker} appended to CSV.\n{df.head()}\n")
            else:
                print(f"No data available for {ticker}.\n")
    except Exception as e:
        print(f"An error occurred: {e}")