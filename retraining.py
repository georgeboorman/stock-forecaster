import pandas as pd
import pickle
from forecast import load_and_split_data, train_model
import mlflow
from datetime import datetime
import pandas as pd
from sklearn.metrics import mean_absolute_error

def train_and_save_model(file_path="stocks.csv", ticker="NVDA", model_path="prophet_model.pkl"):
    # Load and split the data
    train_df, _ = load_and_split_data(file_path, ticker)
    # Train the model
    model = train_model(train_df)
    # Save the model as a pickle file
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f"Model saved to {model_path}")
    # Log retrain time
    retrain_time = datetime.now().isoformat()
    # Evaluate MAE for last 7 days and log with MLflow
    mae = evaluate_mae(file_path=file_path, model_path=model_path, days=7)
    with open("retrain_log.txt", "a") as logf:
        logf.write(f"Retrained at {retrain_time}, MAE: {mae if mae is not None else 'N/A'}\n")
    mlflow.set_experiment("stock_forecaster")
    with mlflow.start_run(run_name=f"retrain_{retrain_time}"):
        mlflow.log_param("ticker", ticker)
        mlflow.log_param("retrain_time", retrain_time)
        if mae is not None:
            mlflow.log_metric("mae_last_7_days", mae)
        mlflow.log_artifact(model_path)
        mlflow.log_artifact(file_path)
        mlflow.log_artifact("retrain_log.txt")


def evaluate_mae(file_path="stocks.csv", model_path="prophet_model.pkl", days=7):
    df = pd.read_csv(file_path)
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    df['ds'] = pd.to_datetime(df['date'])
    df = df.sort_values('ds')
    test_df = df.tail(days)
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
        print(f"MAE for last {days} days: {mae:.4f}")
        return mae
    else:
        print("No overlapping dates for evaluation.")
        return None

if __name__ == "__main__":
    train_and_save_model()
