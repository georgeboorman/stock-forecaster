#!/bin/bash
set -e

# Airflow user setup (if not already created)
# Uncomment lines 6-19 before building the Docker image and running the container if you want to use Airflow within Docker
# airflow users create \
#     --username admin \
#     --firstname Admin \
#     --lastname User \
#     --role Admin \
#     --password password \
#     --email admin@example.com || true

# Initialize Airflow DB
# airflow db init

# Start Airflow webserver and scheduler
# airflow webserver --port 8080 &
# airflow scheduler &

# Start FastAPI
uvicorn app.server:app --host 0.0.0.0 --port 8000 &

# Start MLflow UI
mlflow ui --host 0.0.0.0 --port 5000 --backend-store-uri ./mlruns &

wait