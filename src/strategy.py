import pandas as pd
import numpy as np
from utils.indicators import calculate_sma, calculate_ema, calculate_rsi, calculate_macd, calculate_bollinger_bands

def sma_strategy(data, short_window=40, long_window=100):
    signals = pd.DataFrame(index=data.index)
    signals['price'] = data['Adj Close']
    signals['short_mavg'] = calculate_sma(data['Adj Close'], short_window)
    signals['long_mavg'] = calculate_sma(data['Adj Close'], long_window)
    signals['signal'] = 0.0
    
    signal_start_index = max(short_window, long_window)
    signals['signal'][signal_start_index:] = np.where(
        signals['short_mavg'][signal_start_index:] > signals['long_mavg'][signal_start_index:], 1.0, 0.0
    )
    signals['positions'] = signals['signal'].diff()
    return signals

def ema_strategy(data, short_window=40, long_window=100):
    signals = pd.DataFrame(index=data.index)
    signals['price'] = data['Adj Close']
    signals['short_ema'] = calculate_ema(data['Adj Close'], short_window)
    signals['long_ema'] = calculate_ema(data['Adj Close'], long_window)
    signals['signal'] = 0.0
    
    signal_start_index = max(short_window, long_window)
    signals['signal'][signal_start_index:] = np.where(
        signals['short_ema'][signal_start_index:] > signals['long_ema'][signal_start_index:], 1.0, 0.0
    )
    signals['positions'] = signals['signal'].diff()
    return signals

def rsi_strategy(data, window=14, overbought=70, oversold=30):
    signals = pd.DataFrame(index=data.index)
    signals['price'] = data['Adj Close']
    signals['rsi'] = calculate_rsi(data['Adj Close'], window)
    signals['signal'] = 0.0
    
    signals['signal'] = np.where(signals['rsi'] > overbought, -1.0, np.where(signals['rsi'] < oversold, 1.0, 0.0))
    signals['positions'] = signals['signal'].diff()
    return signals

def macd_strategy(data, short_window=12, long_window=26, signal_window=9):
    signals = pd.DataFrame(index=data.index)
    signals['price'] = data['Adj Close']
    signals['macd'], signals['signal'] = calculate_macd(data['Adj Close'], short_window, long_window, signal_window)
    signals['signal_line'] = 0.0
    
    signals['signal_line'] = np.where(signals['macd'] > signals['signal'], 1.0, 0.0)
    signals['positions'] = signals['signal_line'].diff()
    return signals

def bollinger_bands_strategy(data, window=20, num_std_dev=2):
    signals = pd.DataFrame(index=data.index)
    signals['price'] = data['Adj Close']
    signals['sma'], signals['upper_band'], signals['lower_band'] = calculate_bollinger_bands(data['Adj Close'], window, num_std_dev)
    signals['signal'] = 0.0
    
    signals['signal'] = np.where(signals['price'] < signals['lower_band'], 1.0, np.where(signals['price'] > signals['upper_band'], -1.0, 0.0))
    signals['positions'] = signals['signal'].diff()
    return signals
