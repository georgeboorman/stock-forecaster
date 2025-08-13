# Stock-Forecaster

Stock-Forecaster is an automated pipeline for extracting, forecasting, and evaluating stock prices using Python, Prophet, FastAPI, MLflow, and Airflow.

## Features
- **Data Extraction**: Pulls and appends new stock data from [Twelve Data](https://twelvedata.com/) to `stocks.csv`.
- **Forecasting**: Trains Prophet models to forecast stock prices for Nvidia, Microsoft, and Palantir.
- **API/Deployment**:  - deployed through [Render](https://render.com/) and a FastAPI server; provides a landing page ([here](https://.stock-forecaster-2ubp.onrender.com/)) and an endpoint for forecasting.
- **Automation**: Airflow DAGs automate daily extraction, retraining, and evaluation.
- **Experiment Tracking**: MLflow logs model parameters, metrics (MAE), and artifacts for each retraining run.
- **Jupyter/EDA**: Initial exploratory data analysis in `eda.ipynb`.
- **Docker Support**: Containerized for reproducible deployment.

## Repository Structure
- `extract.py`: Extracts and appends new stock data.
- `forecast.py`: Loads, splits, and trains Prophet models.
- `retraining.py`: Retrains models, evaluates MAE, and logs to MLflow.
- `app/server.py`: FastAPI app for serving forecasts and HTML.
- `client.py`: Example client for API requests.
- `dag.py`: Airflow DAG for daily automation.
- `eda.ipynb`: Exploratory data analysis.
- `stocks.csv`: Main stock data file.
- `requirements.txt`: Python dependencies.
- `Dockerfile`: Container setup.
- `templates/index.html`: HTML for landing page.
- `README.md`: Project documentation.

## Getting Started
### Option 1: Native Python
1. Clone the repo: `git clone https://github.com/georgeboorman/Stock-Forecaster.git`.
2. Create an API key for [Twelve Data](https://twelvedata.com/) and store in a file called `secrets.txt`, e.g., `TWELVE_DATA_API_KEY=<YOUR-API-KEY>`.
3. Optional (recommended) - Create a virtual environment: `python3 -m venv <venv>`.
3. Install dependencies: `pip install -r requirements.txt`.
4. Run extraction: `python3 extract.py`.
5. Train and evaluate: `python3 retraining.py`.
6. Start API: `uvicorn app.server:app --host 0.0.0.0 --port 8000` (press `CTRL+C` to quit).
7. View MLflow UI: `mlflow ui`.
8. (Optional) Set up Airflow for automation.

### Option 2: Docker (Recommended)
1. Clone the repo: `git clone https://github.com/georgeboorman/Stock-Forecaster.git`.
2. Create a `secrets.txt` file with your Twelve Data API key: `TWELVE_DATA_API_KEY=<YOUR-API-KEY>`.
3. Build the Docker image:
   ```sh
   docker build -t <image-name> .
   ```
4. Run the container with an interactive shell, including port mapping:
   ```sh
   docker run -it -p 8000:8000 -p 5000:5000 -p 8080:8080 <image-name>
   ```
   - This exposes FastAPI (8000), MLflow UI (5000), and Airflow (8080) to your host.
5. Inside the container, to start the API:
   ```sh
   uvicorn app.server:app --host 0.0.0.0 --port 8000
   ```
6. Inside the container, to start the MLflow UI:
   ```sh
   mlflow ui --host 0.0.0.0 --port 5000
   ```
7. (Optional) Inside the container, to set up and use Airflow:
   ```sh
   bash airflow_setup.sh
   ```
   - Airflow webserver: [http://localhost:8080](http://localhost:8080)
   - Airflow is not enabled by default; only run this if you want to use Airflow automation.
8. You can also run Python scripts manually inside the container:
   ```sh
   python3 extract.py
   python3 retraining.py
   ```
9. To exit the container shell, type `exit`.

