import pandas as pd
import os
import pickle
from forecast import load_and_split_data, train_model
import mlflow
from datetime import datetime
import pandas as pd
from sklearn.metrics import mean_absolute_error

def train_and_save_model(file_path="stocks.csv", ticker="NVDA", model_path=None):
    # Load and split the data
    train_df, _ = load_and_split_data(file_path, ticker)
    # Train the model
    model = train_model(train_df)
    # Choose best model file name for ticker
    if model_path is None:
        if ticker == "NVDA":
            model_path = "models/prophet_NVDA_prod.pkl"
        elif ticker == "MSFT":
            model_path = "models/prophet_MSFT_prod.pkl"
        elif ticker == "PLTR":
            model_path = "models/prophet_PLTR_prod.pkl"
    # Evaluate MAE for last 7 days
    mae = evaluate_mae(file_path=file_path, ticker=ticker, days=7)
    # Check previous prod model MAE
    prev_mae = None
    if os.path.exists(model_path):
        prev_mae = evaluate_mae(file_path=file_path, ticker=ticker, days=7)
    # If new model is better (lower MAE) or no previous model, save as prod
    if prev_mae is None or (mae is not None and mae < prev_mae):
        with open(model_path, "wb") as f:
            pickle.dump(model, f)
        print(f"New model saved to {model_path} (MAE: {mae:.4f})")
    else:
        print(f"New model not saved to {model_path} (MAE: {mae:.4f} >= previous MAE: {prev_mae:.4f})")
    # Log retrain time
    retrain_time = datetime.now().isoformat()
    with open("retrain_log.txt", "a") as logf:
        logf.write(f"Retrained at {retrain_time}, MAE: {mae if mae is not None else 'N/A'}\n")
    mlflow.set_experiment("stock_forecaster")
    with mlflow.start_run(run_name=f"retrain_{retrain_time}"):
        mlflow.log_param("ticker", ticker)
        mlflow.log_param("retrain_time", retrain_time)
        if mae is not None:
            mlflow.log_metric("mae_last_7_days", mae)
        if prev_mae is not None:
            mlflow.log_metric("prev_mae_last_7_days", prev_mae)
        mlflow.log_artifact(file_path)
        mlflow.log_artifact("retrain_log.txt")


def evaluate_mae(file_path="stocks.csv", ticker="NVDA", days=7):
    if ticker == "NVDA":
        model_path = "models/prophet_NVDA_prod.pkl"
    elif ticker == "MSFT":
        model_path = "models/prophet_MSFT_prod.pkl"
    elif ticker == "PLTR":
        model_path = "models/prophet_PLTR_prod.pkl"
    else:
        raise ValueError(f"Unknown ticker: {ticker}")
    df = pd.read_csv(file_path)
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    df['ds'] = pd.to_datetime(df['date'])
    df = df.sort_values('ds')
    test_df = df[df['ticker'] == ticker].tail(days)
    # Forecast for the actual test dates
    future = pd.DataFrame({'ds': test_df['ds']})
    forecast = model.predict(future)
    forecast = forecast.set_index('ds')
    y_true = []
    y_pred = []
    for _, row in test_df.iterrows():
        date = row['ds']
        actual = row['close']
        if date in forecast.index:
            pred = forecast.loc[date]['yhat']
            # If multiple rows for the same date, take the first
            if isinstance(pred, pd.Series):
                pred = pred.iloc[0]
            y_true.append(actual)
            y_pred.append(pred)
    if y_true:
        mae = mean_absolute_error(y_true, y_pred)
        print(f"MAE for {ticker} in last {days} days: {mae:.4f}")
        return mae
    else:
        print("No overlapping dates for evaluation for {ticker}.")
        return None

if __name__ == "__main__":
    for ticker in ["NVDA", "MSFT", "PLTR"]:
        train_and_save_model(ticker=ticker)
