import pandas as pd
from prophet import Prophet
import pickle
from forecast import load_and_split_data, train_model

def train_and_save_model(file_path="stocks.csv", ticker="NVDA", model_path="prophet_model.pkl"):
    # Load and split the data
    train_df, _ = load_and_split_data(file_path, ticker)
    # Train the model
    model = train_model(train_df)
    # Save the model as a pickle file
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_and_save_model()
