import numpy as np
import pandas as pd

def generate_bitcoin_prices():
    """
    Generates 60 days of simulated Bitcoin price data using a
    Geometric Brownian Motion model.
    """
    # Parameters
    initial_price = 50000  # Starting Bitcoin price
    mu = 0.001  # Average daily return (drift)
    sigma = 0.03  # Daily volatility
    days = 60

    # Generate daily returns
    daily_returns = np.random.normal(mu, sigma, days)

    # Generate price path
    prices = [initial_price]
    for r in daily_returns:
        prices.append(prices[-1] * (1 + r))

    # Create a pandas DataFrame
    price_data = pd.DataFrame({
        'Date': pd.to_datetime(pd.date_range(start='2023-01-01', periods=days)),
        'Price': prices[1:]
    })
    price_data.set_index('Date', inplace=True)
    return price_data

def calculate_moving_averages(price_data):
    """
    Calculates the 7-day and 30-day moving averages.
    """
    price_data['MA7'] = price_data['Price'].rolling(window=7).mean()
    price_data['MA30'] = price_data['Price'].rolling(window=30).mean()
    return price_data

def implement_trading_algorithm(data):
    """
    Implements the Golden Cross trading algorithm.
    - Generates a 'Buy' signal when the 7-day MA crosses above the 30-day MA.
    - Generates a 'Sell' signal when the 7-day MA crosses below the 30-day MA.
    """
    data['Signal'] = np.where(data['MA7'] > data['MA30'], 1, 0)
    data['Position'] = data['Signal'].diff()
    return data

def simulate_trading(data):
    """
    Simulates trading based on the Golden Cross algorithm and prints a daily ledger.
    """
    initial_cash = 100000.0
    cash = initial_cash
    btc_holdings = 0.0
    portfolio_value = initial_cash

    print("------ Trading Simulation Ledger ------")
    print(f"{'Date':<12} | {'Price':<15} | {'Action':<6} | {'Cash':<15} | {'BTC':<15} | {'Portfolio Value':<20}")
    print("-" * 90)

    for i in range(len(data)):
        date = data.index[i].strftime('%Y-%m-%d')
        price = data['Price'].iloc[i]
        signal = data['Position'].iloc[i]
        action = 'Hold'

        # Buy signal
        if signal == 1:
            if cash > 0:
                btc_to_buy = cash / price
                btc_holdings += btc_to_buy
                cash = 0
                action = 'Buy'
        # Sell signal
        elif signal == -1:
            if btc_holdings > 0:
                cash += btc_holdings * price
                btc_holdings = 0
                action = 'Sell'

        portfolio_value = cash + (btc_holdings * price)
        print(f"{date:<12} | {price:<15.2f} | {action:<6} | {cash:<15.2f} | {btc_holdings:<15.6f} | {portfolio_value:<20.2f}")

    return initial_cash, portfolio_value

if __name__ == "__main__":
    prices = generate_bitcoin_prices()
    data = calculate_moving_averages(prices)
    data = implement_trading_algorithm(data)
    initial_cash, portfolio_value = simulate_trading(data)

    # --- Final Portfolio Performance ---
    profit = portfolio_value - initial_cash
    profit_percentage = (profit / initial_cash) * 100

    print("\n------ Final Portfolio Performance ------")
    print(f"Initial Portfolio Value: ${initial_cash:,.2f}")
    print(f"Final Portfolio Value:   ${portfolio_value:,.2f}")
    print(f"Profit/Loss:             ${profit:,.2f}")
    print(f"Return on Investment:    {profit_percentage:.2f}%")
    print("---------------------------------------")
