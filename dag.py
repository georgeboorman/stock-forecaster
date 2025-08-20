from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess
import os
import sys
from retraining import evaluate_mae

today = datetime.today().strftime("%Y-%m-%d")

BASE_DIR = os.environ.get("BASE_DIR")
sys.path.append(BASE_DIR)
EXTRACT_SCRIPT = os.path.join(BASE_DIR, 'extract.py')
DATA_PATH = os.path.join(BASE_DIR, 'stocks.csv')

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 8, 12),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def run_extract():
    subprocess.run(['python3', EXTRACT_SCRIPT], check=True, cwd=BASE_DIR)

def retrain_model():
    # Retrain models for all tickers
    import retraining
    for ticker in ["NVDA", "MSFT", "PLTR"]:
        retraining.train_and_save_model(ticker=ticker)

def evaluate_model():
    # Evaluate models for all tickers
    import retraining
    for ticker in ["NVDA", "MSFT", "PLTR"]:
        # No longer required due to changes in retraining.py
        # if ticker == "NVDA":
        #     model_path = os.path.join(BASE_DIR, "models/prophet_NVDA_prod.pkl")
        # elif ticker == "MSFT":
        #     model_path = os.path.join(BASE_DIR, "models/prophet_MSFT_prod.pkl")
        # elif ticker == "PLTR":
        #     model_path = os.path.join(BASE_DIR, "models/prophet_PLTR_prod.pkl")
        retraining.evaluate_mae(file_path=DATA_PATH, ticker=ticker, days=7)

def git_commit_and_push():
    import subprocess
    # Add updated files
    subprocess.run(['git', 'add', 'stocks.csv'], check=True, cwd=BASE_DIR)
    subprocess.run(['git', 'add', 'models/'], check=True, cwd=BASE_DIR)
    # Commit changes
    subprocess.run(['git', 'commit', '-m', f'Update data and models from Airflow DAG ({today})'], check=False, cwd=BASE_DIR)
    # Push to remote
    subprocess.run(['git', 'push', 'origin', 'main'], check=False, cwd=BASE_DIR)

dag = DAG(
    'stock_forecaster_retrain_eval',
    default_args=default_args,
    description='Extract new data, retrain Prophet model, and evaluate MAE on new data',
    schedule_interval='0 9 * * *',  # daily at 9am
    catchup=True,
)

extract_task = PythonOperator(
    task_id='run_extract',
    python_callable=run_extract,
    dag=dag,
)

retrain_task = PythonOperator(
    task_id='retrain_model',
    python_callable=retrain_model,
    dag=dag,
)

evaluate_task = PythonOperator(
    task_id='evaluate_model',
    python_callable=evaluate_model,
    dag=dag,
)

git_task = PythonOperator(
    task_id='git_commit_and_push',
    python_callable=git_commit_and_push,
    dag=dag,
)

extract_task >> retrain_task >> evaluate_task >> git_task