from flask import Flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from utils.data_loader import load_data, preprocess_data
from strategy import sma_strategy, ema_strategy, rsi_strategy, macd_strategy, bollinger_bands_strategy
from utils.performance import calculate_performance

# Flask app
server = Flask(__name__)

# Dash app
app = dash.Dash(__name__, server=server, url_base_pathname='/')

app.layout = html.Div([
    html.H1("Algo Trading Backtest"),
    html.Div([
        html.Label('Ticker:'),
        dcc.Input(id='ticker', value='AAPL', type='text'),
    ]),
    html.Div([
        html.Label('Start Date:'),
        dcc.Input(id='start_date', value='2015-01-01', type='text'),
    ]),
    html.Div([
        html.Label('End Date:'),
        dcc.Input(id='end_date', value='2020-01-01', type='text'),
    ]),
    html.Div([
        html.Label('Short Window:'),
        dcc.Input(id='short_window', value=40, type='number'),
    ]),
    html.Div([
        html.Label('Long Window:'),
        dcc.Input(id='long_window', value=100, type='number'),
    ]),
    html.Div([
        html.Label('Strategy:'),
        dcc.Dropdown(
            id='strategy',
            options=[
                {'label': 'Simple Moving Average (SMA)', 'value': 'sma'},
                {'label': 'Exponential Moving Average (EMA)', 'value': 'ema'},
                {'label': 'Relative Strength Index (RSI)', 'value': 'rsi'},
                {'label': 'Moving Average Convergence Divergence (MACD)', 'value': 'macd'},
                {'label': 'Bollinger Bands', 'value': 'bollinger_bands'}
            ],
            value='sma'
        ),
    ]),
    html.Button('Run Backtest', id='run_backtest', n_clicks=0),
    dcc.Graph(id='price_chart'),
    html.Div(id='performance_metrics')
])

@app.callback(
    [Output('price_chart', 'figure'),
     Output('performance_metrics', 'children')],
    [Input('run_backtest', 'n_clicks')],
    [dash.dependencies.State('ticker', 'value'),
     dash.dependencies.State('start_date', 'value'),
     dash.dependencies.State('end_date', 'value'),
     dash.dependencies.State('short_window', 'value'),
     dash.dependencies.State('long_window', 'value'),
     dash.dependencies.State('strategy', 'value')]
)
def update_graph(n_clicks, ticker, start_date, end_date, short_window, long_window, strategy):
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
    else:
        return go.Figure(), "Invalid strategy selected"

    performance = calculate_performance(data, signals)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Adj Close'], mode='lines', name='Price'))
    
    if 'short_mavg' in signals.columns:
        fig.add_trace(go.Scatter(x=signals.index, y=signals['short_mavg'], mode='lines', name='Short SMA'))
    if 'long_mavg' in signals.columns:
        fig.add_trace(go.Scatter(x=signals.index, y=signals['long_mavg'], mode='lines', name='Long SMA'))
    if 'short_ema' in signals.columns:
        fig.add_trace(go.Scatter(x=signals.index, y=signals['short_ema'], mode='lines', name='Short EMA'))
    if 'long_ema' in signals.columns:
        fig.add_trace(go.Scatter(x=signals.index, y=signals['long_ema'], mode='lines', name='Long EMA'))
    if 'rsi' in signals.columns:
        fig.add_trace(go.Scatter(x=signals.index, y=signals['rsi'], mode='lines', name='RSI'))
    if 'macd' in signals.columns:
        fig.add_trace(go.Scatter(x=signals.index, y=signals['macd'], mode='lines', name='MACD'))
    if 'signal' in signals.columns and strategy == 'macd':
        fig.add_trace(go.Scatter(x=signals.index, y=signals['signal'], mode='lines', name='MACD Signal'))
    if 'upper_band' in signals.columns and 'lower_band' in signals.columns:
        fig.add_trace(go.Scatter(x=signals.index, y=signals['upper_band'], mode='lines', name='Upper Bollinger Band'))
        fig.add_trace(go.Scatter(x=signals.index, y=signals['lower_band'], mode='lines', name='Lower Bollinger Band'))
    
    if 'positions' in signals.columns:
        buy_signals = signals.loc[signals.positions == 1.0]
        sell_signals = signals.loc[signals.positions == -1.0]
        fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['price'], mode='markers', marker=dict(color='green', symbol='triangle-up', size=10), name='Buy Signal'))
        fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['price'], mode='markers', marker=dict(color='red', symbol='triangle-down', size=10), name='Sell Signal'))

    performance_metrics = [
        html.P(f"Cumulative Return: {performance['cumulative_return']:.2%}"),
        # Aggiungi altre metriche di performance qui se necessario
    ]
    
    return fig, performance_metrics

if __name__ == '__main__':
    app.run_server(debug=True)
