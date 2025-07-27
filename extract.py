import requests
import pandas as pd
import psycopg2
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

def authenticate_db(filepath='secrets.txt'):
    """
    Authenticates and returns a PostgreSQL connection and cursor.
    Raises an exception if connection fails.
    """
    creds = {}
    with open(filepath, 'r') as file:
        for line in file:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                creds[k] = v
    try:
        conn = psycopg2.connect(
            dbname=creds.get('POSTGRES_DB_NAME', 'stock_data'),
            user=creds.get('POSTGRES_USER', 'postgres'),
            password=creds.get('POSTGRES_PASSWORD', ''),
            host=creds.get('POSTGRES_HOST', 'localhost'),
            port=creds.get('POSTGRES_PORT', '5432')
        )
        cur = conn.cursor()
        return conn, cur
    except Exception as e:
        raise ConnectionError(f"Failed to connect to PostgreSQL: {e}")
    


def get_stock_data(tickers, api_key, interval='1day', outputsize=5):
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
            df['ticker'] = ticker
            df['datetime'] = pd.to_datetime(df['datetime'])
            # Convert columns to float
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            result[ticker] = df
        else:
            print(f"Error fetching data for {ticker}: {data.get('message', 'Unknown error')}")
            result[ticker] = None
    return result

def update_db(data_dict, conn, cur, table_name="stock_prices"):
    """
    Updates the database with new data from the API.
    """
    for ticker, df in data_dict.items():
        if df is not None:
            for _, row in df.iterrows():
                cur.execute(f"""
                    INSERT INTO {table_name} (ticker, datetime, open, high, low, close, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (ticker, datetime) DO NOTHING;
                """, (row['ticker'], row['datetime'], row['open'], row['high'], row['low'], row['close'], row['volume']))
    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    try:
        api_key = read_api_key()
        conn, cur = authenticate_db()
        tickers = ['NVDA', 'PLTR']
        stock_data = get_stock_data(tickers, api_key)
        update_db(stock_data, conn, cur)
        for ticker, df in stock_data.items():
            if df is not None:
                print(f"Data for {ticker} inserted into database.\n{df.head()}\n")
            else:
                print(f"No data available for {ticker}.\n")
    except Exception as e:
        print(f"An error occurred: {e}")