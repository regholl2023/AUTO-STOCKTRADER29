import numpy as np

def calculate_performance(data, signals):
    signals['portfolio'] = signals['positions'].shift() * data['Return']
    signals['cumulative_return'] = (1 + signals['portfolio']).cumprod() - 1
    performance = {
        'cumulative_return': signals['cumulative_return'].iloc[-1]
    }
    return performance
