import matplotlib.pyplot as plt
from utils.data_loader import load_data, preprocess_data
from strategy import sma_strategy
from utils.performance import calculate_performance

def main():
    ticker = 'BTC-USD'
    '''start_date = '2015-01-01'
    end_date = '2020-01-01'''
    start_date = '2020-01-01'
    end_date = '2024-06-27'

    data = load_data(ticker, start_date, end_date)
    data = preprocess_data(data)

    signals = sma_strategy(data)

    performance = calculate_performance(data, signals)
    print(f"Cumulative Return: {performance['cumulative_return']:.2f}")

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(data['Adj Close'], label='Price')
    ax.plot(signals['short_mavg'], label='40-day SMA')
    ax.plot(signals['long_mavg'], label='100-day SMA')

    ax.plot(signals.loc[signals.positions == 1.0].index, 
             signals.short_mavg[signals.positions == 1.0],
             '^', markersize=10, color='m', label='buy')
    ax.plot(signals.loc[signals.positions == -1.0].index, 
             signals.short_mavg[signals.positions == -1.0],
             'v', markersize=10, color='k', label='sell')

    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()
