from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess
import os
import sys

BASE_DIR = os.getcwd()
sys.path.append(BASE_DIR)
DATA_PATH = os.path.join(BASE_DIR, 'stocks.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'prophet_model.pkl')
EXTRACT_SCRIPT = os.path.join(BASE_DIR, 'extract.py')
TRAIN_SCRIPT = os.path.join(BASE_DIR, 'retraining.py')

from retraining import evaluate_mae

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 8, 12),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def run_extract():
    subprocess.run(['python3', EXTRACT_SCRIPT], check=True)

def retrain_model():
    subprocess.run(['python3', TRAIN_SCRIPT], check=True)

def evaluate_model():
    evaluate_mae(file_path=DATA_PATH, model_path=MODEL_PATH, days=7)

dag = DAG(
    'stock_forecaster_retrain_eval',
    default_args=default_args,
    description='Extract new data, retrain Prophet model, and evaluate MAE on new data',
    schedule_interval='0 9 * * *',  # daily at 9am
    catchup=False,
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

extract_task >> retrain_task >> evaluate_task