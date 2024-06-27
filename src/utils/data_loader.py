import yfinance as yf
import pandas as pd

def load_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

def preprocess_data(data):
    data['Return'] = data['Adj Close'].pct_change()
    data.dropna(inplace=True)
    return data
