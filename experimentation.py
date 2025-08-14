import pandas as pd
import pickle
import mlflow
from prophet import Prophet
from datetime import datetime

def run_experiment(file_path="stocks.csv", ticker="NVDA", param_grid=None, model_dir="models"):
    if param_grid is None:
        param_grid = [
            # changepoint_prior_scale controls the flexibility of the trend
            # seasonality_prior_scale controls the flexibility of the seasonality - left static as there is no seasonality
            {"changepoint_prior_scale": 0.01, "seasonality_prior_scale": 1.0},
            {"changepoint_prior_scale": 0.05, "seasonality_prior_scale": 1.0},
            {"changepoint_prior_scale": 0.1, "seasonality_prior_scale": 1.0},
            {"changepoint_prior_scale": 0.25, "seasonality_prior_scale": 1.0},
            {"changepoint_prior_scale": 0.5, "seasonality_prior_scale": 1.0},
            {"changepoint_prior_scale": 0.8, "seasonality_prior_scale": 1.0}
        ]
    df = pd.read_csv(file_path)
    df = df[df["ticker"] == ticker]
    df = df.rename(columns={"date": "ds", "close": "y"})
    df["ds"] = pd.to_datetime(df["ds"])
    df = df.sort_values("ds")
    train_df = df.copy()
    mlflow.set_experiment("prophet_hyperparam_experiments")
    for i, params in enumerate(param_grid):
        run_name = f"{ticker}_run_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with mlflow.start_run(run_name=run_name):
            model = Prophet(
                changepoint_prior_scale=params["changepoint_prior_scale"],
                seasonality_prior_scale=params["seasonality_prior_scale"]
            )
            model.fit(train_df)
            # Save model
            model_path = f"{model_dir}/prophet_{ticker}_run_{i}.pkl"
            with open(model_path, "wb") as f:
                pickle.dump(model, f)
            mlflow.log_params(params)
            mlflow.log_param("ticker", ticker)
            mlflow.log_artifact(model_path)
            # Evaluate MAE on last 7 days
            test_df = train_df.tail(7)
            future = pd.DataFrame({"ds": test_df["ds"]})
            forecast = model.predict(future)
            forecast = forecast.set_index("ds")
            y_true = test_df["y"].values
            y_pred = forecast.loc[test_df["ds"]]["yhat"].values
            if len(y_true) == len(y_pred):
                mae = ((y_true - y_pred) ** 2).mean() ** 0.5
                mlflow.log_metric("mae_last_7_days", mae)
            else:
                mlflow.log_metric("mae_last_7_days", None)
            print(f"Run {i} for {ticker}: params={params}, MAE={mae if len(y_true)==len(y_pred) else 'N/A'}")

if __name__ == "__main__":
    for ticker in ["NVDA", "MSFT", "PLTR"]:
        run_experiment(ticker=ticker)
