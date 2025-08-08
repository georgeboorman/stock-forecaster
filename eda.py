import pandas as pd
import plotly.express as px

df = pd.read_csv('stocks.csv')

def plot_all_stocks(df):
    """
    Plots stock data for all tickers in the data_dict.

    Parameters:
        data_dict (dict): Dictionary of DataFrames keyed by ticker symbol

    Returns:
        None: Displays the plot
    """

    fig = px.line(df, x="date", y="close", color="ticker",
                  title="Stock Prices Over Time",
                  labels={"date": "Date", "close": "Closing Price", "ticker": "Ticker Symbol"})
    fig.update_layout(xaxis_title="Date", yaxis_title="Closing Price")
    fig.show()

if __name__ == "__main__":
    plot_all_stocks(df)