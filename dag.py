from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess

# Import evaluation function from train_and_save_model.py
import sys
sys.path.append(BASE_DIR)
from retraining import evaluate_mae


# Paths
import os
BASE_DIR = os.getcwd()
import sys
sys.path.append(BASE_DIR)
DATA_PATH = os.path.join(BASE_DIR, 'stocks.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'prophet_model.pkl')
TRAIN_SCRIPT = os.path.join(BASE_DIR, 'train_and_save_model.py')

# Default args for Airflow
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 8, 12),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def retrain_model():
    subprocess.run(['python3', TRAIN_SCRIPT], check=True)

def evaluate_model():
    # Call the evaluation function from train_and_save_model.py
    evaluate_mae(file_path=DATA_PATH, model_path=MODEL_PATH, days=7)

dag = DAG(
    'stock_forecaster_retrain_eval',
    default_args=default_args,
    description='Retrain Prophet model and evaluate MAE on new data',
    schedule_interval='@daily',
    catchup=False,
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

retrain_task >> evaluate_task
