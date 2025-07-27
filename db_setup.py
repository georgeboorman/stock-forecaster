import psycopg2
import pandas as pd

DB_NAME = "stock_data"
DB_USER = "postgres"
DB_PASSWORD = "your_password"  # Change as needed
DB_HOST = "localhost"
DB_PORT = "5432"
TABLE_NAME = "stock_prices"

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    datetime TIMESTAMP NOT NULL,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume FLOAT
);
"""

def setup_database():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()
    cur.execute(CREATE_TABLE_SQL)
    conn.commit()
    cur.close()
    conn.close()

def load_csv_to_db(csv_path, ticker):
    df = pd.read_csv(csv_path)
    df['ticker'] = ticker
    df['datetime'] = pd.to_datetime(df['datetime'])
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()
    for _, row in df.iterrows():
        cur.execute(f"""
            INSERT INTO {TABLE_NAME} (ticker, datetime, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (ticker, datetime) DO NOTHING;
        """, (row['ticker'], row['datetime'], row['open'], row['high'], row['low'], row['close'], row['volume']))
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    setup_database()
    load_csv_to_db("NVDA_data.csv", "NVDA")
    load_csv_to_db("PLTR_data.csv", "PLTR")
    print("Database setup and CSVs loaded.")
