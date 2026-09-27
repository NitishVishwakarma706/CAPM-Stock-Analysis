import yfinance as yf
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
import numpy as np
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import pandas as pd

def get_data(ticker):
    end_date = datetime.now().strftime('%Y-%m-%d')
    stock_data = yf.download(ticker, start='2024-01-01', end=end_date)
    return stock_data[['Close']]

def stationary_check(close_price):
    series = np.array(close_price).flatten()
    adf_test = adfuller(series)
    p_value = round(adf_test[1], 3)
    return p_value

def get_rolling_mean(close_price):
    rolling_price = close_price.rolling(window=7).mean().dropna()
    return rolling_price

def get_differencing_order(close_price):
    working_series = close_price.copy()
    p_value = stationary_check(working_series)
    d = 0
    
    while p_value > 0.05 and d < 2:
        d += 1
        working_series = working_series.diff().dropna()
        p_value = stationary_check(working_series)
        
    return d

def fit_model(data, differencing_order):
    flat_data = np.array(data).flatten()
    
    model = ARIMA(flat_data, order=(5, differencing_order, 5))
    model_fit = model.fit()

    forecast_step = 30
    forecast = model_fit.get_forecast(steps=forecast_step)
    return forecast.predicted_mean

def evaluate_model(scaled_data, differencing_order):
    train_data, test_data = scaled_data[:-30], scaled_data[-30:]
    prediction = fit_model(train_data, differencing_order)
    
    rmse = np.sqrt(mean_squared_error(test_data, prediction))
    return round(rmse, 2)

def scaling(close_price):
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(np.array(close_price).reshape(-1, 1))
    return scaled_data, scaler

def get_forcast(scaled_data, differencing_order):
    prediction = fit_model(scaled_data, differencing_order)
    
    start_date = datetime.now() + timedelta(days=1)
    forecast_index = pd.date_range(start=start_date, periods=30, freq='D')
    
    forecast_df = pd.DataFrame(prediction.reshape(-1, 1), index=forecast_index, columns=['Close'])
    return forecast_df

def inverse_scaling(scaler, scaled_series):
    raw_array = np.array(scaled_series).reshape(-1, 1)
    unscaled_data = scaler.inverse_transform(raw_array)
    return unscaled_data.flatten()

