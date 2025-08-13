#!/bin/bash
set -e

# Airflow user setup (if not already created)
# Change your details as needed
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --password password \
    --email admin@example.com || true

# Initialize Airflow DB
airflow db init

# Start Airflow webserver and scheduler
airflow webserver --port 8080 &
airflow scheduler & 

wait