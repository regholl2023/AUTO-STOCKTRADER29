from turtle import pd
from flask import Flask, request, jsonify, render_template, send_file
import os
import matplotlib.pyplot as plt
from utils.data_loader import load_data, preprocess_data
from strategy import sma_strategy, ema_strategy, rsi_strategy, macd_strategy, bollinger_bands_strategy
from utils.performance import calculate_performance
from models.model import train_lstm

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/backtest', methods=['GET'])
def backtest():
    ticker = request.args.get('ticker', 'AAPL')
    start_date = request.args.get('start_date', '2015-01-01')
    end_date = request.args.get('end_date', '2020-01-01')
    strategy = request.args.get('strategy', 'sma')
    
    try:
        short_window = int(request.args.get('short_window', 40))
        long_window = int(request.args.get('long_window', 100))
    except TypeError:
        return jsonify({"error": "Invalid input for short_window or long_window"}), 400

    data = load_data(ticker, start_date, end_date)
    data = preprocess_data(data)
    
    if strategy == 'sma':
        signals = sma_strategy(data, short_window, long_window)
    elif strategy == 'ema':
        signals = ema_strategy(data, short_window, long_window)
    elif strategy == 'rsi':
        signals = rsi_strategy(data)
    elif strategy == 'macd':
        signals = macd_strategy(data)
    elif strategy == 'bollinger_bands':
        signals = bollinger_bands_strategy(data)
    elif strategy == 'lstm':
        model, scaler, train_predict, test_predict = train_lstm(data)
        signals = pd.DataFrame(data={'price': data['Adj Close'], 'train_predict': train_predict.flatten(), 'test_predict': test_predict.flatten()}, index=data.index)
    else:
        return jsonify({"error": "Invalid strategy selected"}), 400

    performance = calculate_performance(data, signals)
    plot_path = create_plot(data, signals, ticker, strategy)
    
    result = {
        'ticker': ticker,
        'start_date': start_date,
        'end_date': end_date,
        'strategy': strategy,
        'short_window': short_window,
        'long_window': long_window,
        'cumulative_return': performance['cumulative_return'],
        'plot_path': plot_path
    }
    
    return render_template('index.html', result=result)

def create_plot(data, signals, ticker, strategy):
    plt.figure(figsize=(10, 6))
    plt.plot(data['Adj Close'], label='Price')
    if 'short_mavg' in signals.columns:
        plt.plot(signals['short_mavg'], label='Short SMA')
    if 'long_mavg' in signals.columns:
        plt.plot(signals['long_mavg'], label='Long SMA')
    if 'short_ema' in signals.columns:
        plt.plot(signals['short_ema'], label='Short EMA')
    if 'long_ema' in signals.columns:
        plt.plot(signals['long_ema'], label='Long EMA')
    if 'rsi' in signals.columns:
        plt.plot(signals['rsi'], label='RSI')
    if 'macd' in signals.columns:
        plt.plot(signals['macd'], label='MACD')
    if 'signal' in signals.columns and strategy == 'macd':
        plt.plot(signals['signal'], label='MACD Signal')
    if 'upper_band' in signals.columns and 'lower_band' in signals.columns:
        plt.plot(signals['upper_band'], label='Upper Bollinger Band')
        plt.plot(signals['lower_band'], label='Lower Bollinger Band')
    if 'train_predict' in signals.columns and 'test_predict' in signals.columns:
        plt.plot(signals.index, signals['train_predict'], label='Train Predict')
        plt.plot(signals.index, signals['test_predict'], label='Test Predict')
    if 'positions' in signals.columns:
        plt.plot(signals.loc[signals.positions == 1.0].index, 
                 signals.price[signals.positions == 1.0],
                 '^', markersize=10, color='g', label='Buy Signal')
        plt.plot(signals.loc[signals.positions == -1.0].index, 
                 signals.price[signals.positions == -1.0],
                 'v', markersize=10, color='r', label='Sell Signal')
    plt.title(f'{ticker} Price and {strategy.upper()} Strategy')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plot_path = f'static/{ticker}_{strategy}_plot.png'
    plt.savefig(plot_path)
    plt.close()
    return plot_path

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True)
