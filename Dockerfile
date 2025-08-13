# Use official Python 3.10 base image
FROM python:3.10-slim

# Set working directory
WORKDIR /code

# Install system dependencies
RUN apt-get update && \
    apt-get install -y wget build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set up Airflow environment
ENV AIRFLOW_HOME=/code/airflow
ENV AIRFLOW__CORE__DAGS_FOLDER=/code/dags
COPY dag.py /code/dags/

# Expose ports for FastAPI, MLflow, and Airflow
EXPOSE 8000 5000 8080

CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]