import os
import pandas as pd
from binance.client import Client
import time
import argparse

def fetch_historical_data(client, symbol, interval, lookback="30 days ago UTC"):
    """
    Fetches historical klines from Binance and returns a pandas DataFrame.
    """
    try:
        klines = client.futures_historical_klines(symbol, interval, lookback)
        data = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
        data.set_index('timestamp', inplace=True)
        data['close'] = data['close'].astype(float)
        return data
    except Exception as e:
        print(f"An error occurred while fetching historical data: {e}")
        return None

def calculate_moving_averages(data):
    """Calculates the 7-day and 30-day moving averages."""
    data['MA7'] = data['close'].rolling(window=7).mean()
    data['MA30'] = data['close'].rolling(window=30).mean()
    return data

def execute_trade(client, symbol, side, quantity):
    """
    Executes a trade on Binance.
    For safety, this uses create_test_order.
    Replace with create_order for live trading.
    """
    try:
        print(f"Submitting Futures test order: {side} {quantity} {symbol}")
        order = client.futures_create_test_order(
            symbol=symbol,
            side=side,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity
        )
        print("Test order successful.")
        return order
    except Exception as e:
        print(f"An error occurred while executing trade: {e}")
        return None

def run_trading_bot():
    """Main function to run the trading bot."""
    parser = argparse.ArgumentParser(description='Binance Futures Trading Bot')
    parser.add_argument('--symbol', type=str, default='BTCUSDT', help='Trading symbol (e.g., BTCUSDT)')
    args = parser.parse_args()
    symbol = args.symbol

    # It's crucial to securely manage your API keys.
    # Never hardcode them in your script.
    api_key = os.environ.get('BINANCE_API_KEY')
    api_secret = os.environ.get('BINANCE_API_SECRET')

    if not api_key or not api_secret:
        print("Error: Binance API keys not found.")
        print("Please set the BINANCE_API_KEY and BINANCE_API_SECRET environment variables.")
        return

    client = Client(api_key, api_secret, testnet=True)
    client.API_URL = 'https://testnet.binancefuture.com/fapi'
    interval = Client.KLINE_INTERVAL_1DAY
    quantity = 0.001  # Example quantity

    position_held = False  # Track if we are in a long position

    while True:
        try:
            data = fetch_historical_data(client, symbol, interval)
            if data is not None and not data.empty:
                data = calculate_moving_averages(data)
                last_row = data.iloc[-1]

                # Golden Cross: MA7 crosses above MA30
                if last_row['MA7'] > last_row['MA30'] and not position_held:
                    print("Golden Cross detected. Placing BUY order.")
                    execute_trade(client, symbol, Client.SIDE_BUY, quantity)
                    position_held = True
                # Death Cross: MA7 crosses below MA30
                elif last_row['MA7'] < last_row['MA30'] and position_held:
                    print("Death Cross detected. Placing SELL order.")
                    execute_trade(client, symbol, Client.SIDE_SELL, quantity)
                    position_held = False
                else:
                    print("No trading signal. Holding position.")
        except Exception as e:
            print(f"An error occurred in the main loop: {e}")

        time.sleep(60)

if __name__ == "__main__":
    run_trading_bot()
