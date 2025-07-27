import requests
import pandas as pd

# Function to read API key from secrets.txt
def read_api_key(filepath='secrets.txt', key_name='TWELVE_DATA_API_KEY'):
    with open(filepath, 'r') as file:
        for line in file:
            if line.strip().startswith(key_name + '='):
                return line.strip().split('=')[1]
    raise ValueError(f"{key_name} not found in {filepath}")

# for greater simplicity install our package
# https://github.com/twelvedata/twelvedata-python

import requests

response = requests.get("https://api.twelvedata.com/time_series?apikey=1c7303e404eb418485c1023acd179f64&interval=1min&symbol=NVDA&type=stock&outputsize=5&start_date=2025-07-24 00:00:00&end_date=2025-07-25 00:00:00&format=CSV")

print(response.text)
    

def get_stock_data_from_twelvedata(tickers, api_key, interval='1day', outputsize=5):
    """
    Fetch historical stock data from Twelve Data API and return as a dict of DataFrames.

    Parameters:
        tickers (list): List of stock symbols (e.g., ['NVDA', 'PLTR'])
        api_key (str): Your Twelve Data API key
        interval (str): Data interval (e.g., '1min', '5min', '1day')
        outputsize (int): Number of data points to fetch

    Returns:
        dict: Dictionary of DataFrames keyed by ticker symbol
    """
    base_url = "https://api.twelvedata.com/time_series"
    result = {}

    for ticker in tickers:
        params = {
            'symbol': ticker,
            'interval': interval,
            'outputsize': outputsize,
            'apikey': api_key
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if "values" in data:
            df = pd.DataFrame(data['values'])
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.set_index('datetime')
            df = df.sort_index()
            df = df.astype(float)  # Convert all columns to numeric

            # Save to CSV file
            csv_filename = f"{ticker}_data.csv"
            df.to_csv(csv_filename)

            result[ticker] = df
        else:
            print(f"Error fetching data for {ticker}: {data.get('message', 'Unknown error')}")
            result[ticker] = None

    return result

if __name__ == "__main__":
    # Example usage
    try:
        api_key = read_api_key()
        tickers = ['NVDA', 'PLTR']
        stock_data = get_stock_data_from_twelvedata(tickers, api_key)

        for ticker, df in stock_data.items():
            if df is not None:
                print(f"Data for {ticker}:\n{df.head()}\n")
            else:
                print(f"No data available for {ticker}.\n")
    except Exception as e:
        print(f"An error occurred: {e}")