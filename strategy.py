import pandas as pd
import pandas_datareader as web
import numpy as np
import scipy.optimize as sci_opt
import csv
import matplotlib.pyplot as plt
from portfolio import portfolio

# disable copy warnings
pd.options.mode.chained_assignment = None  # default='warn'

# train vars
symbols = ["VGT", "GLD"]
benchmark = "^GSPC"
start_date_train = '2007/01/01'
end_date_train = '2015/11/01'
start_date_strategy = '2007-11-01'
end_date_strategy = '2021-11-01'
interval = 'm'
num_periods = 12
number_of_symbols = len(symbols)

# strategy vars
risk_free_rate = 0.001
strategy_name = 'Rebalance half year'
start_balance = 1000
buy_monthly = 1000
months_rebalance = 6

try:
    data = web.get_data_yahoo(symbols, start_date_train, end_date_strategy, interval = interval)['Adj Close']
    # print(data)
except Exception as e:
    print('Something went wrong with getting data:', e)

price_data_frame = data.loc[start_date_train:end_date_train]
df_to_csv = price_data_frame.pct_change()
df_to_csv.to_excel('./data_voor_excel.xlsx', sheet_name='data')

# Calculate the Log of returns.
log_return = np.log(1 + price_data_frame.pct_change())

# Initialize the components, to run a Monte Carlo Simulation.

# We will run 5000 iterations.
num_of_portfolios = 5000

# Prep an array to store the weights as they are generated, 5000 iterations for each of our 4 symbols.
all_weights = np.zeros((num_of_portfolios, number_of_symbols))

# Prep an array to store the returns as they are generated, 5000 possible return values.
ret_arr = np.zeros(num_of_portfolios)

# Prep an array to store the volatilities as they are generated, 5000 possible volatility values.
vol_arr = np.zeros(num_of_portfolios)

# Prep an array to store the sharpe ratios as they are generated, 5000 possible Sharpe Ratios.
sharpe_arr = np.zeros(num_of_portfolios)

# Start the simulations.
for ind in range(num_of_portfolios):

    # First, calculate the weights.
    weights = np.array(np.random.random(number_of_symbols))
    weights = weights / np.sum(weights)

    # Add the weights, to the `weights_arrays`.
    all_weights[ind, :] = weights

    # Calculate the expected log returns, and add them to the `returns_array`.
    ret_arr[ind] = np.sum((log_return.mean() * weights) * num_periods)

    # Calculate the volatility, and add them to the `volatility_array`.
    vol_arr[ind] = np.sqrt(
        np.dot(weights.T, np.dot(log_return.cov() * num_periods, weights))
    )

    # Calculate the Sharpe Ratio and Add it to the `sharpe_ratio_array`.
    sharpe_arr[ind] = (ret_arr[ind] - risk_free_rate)/vol_arr[ind]

# Let's create our "Master Data Frame", with the weights, the returns, the volatility, and the Sharpe Ratio
simulations_data = [ret_arr, vol_arr, sharpe_arr, all_weights]

# Create a DataFrame from it, then Transpose it so it looks like our original one.
simulations_df = pd.DataFrame(data=simulations_data).T

# Give the columns the Proper Names.
simulations_df.columns = [
    'Returns',
    'Volatility',
    'Sharpe Ratio',
    'Portfolio Weights'
]

# Make sure the data types are correct, we don't want our floats to be strings.
simulations_df = simulations_df.infer_objects()

# Return the Max Sharpe Ratio from the run.
max_sharpe_ratio = simulations_df.loc[simulations_df['Sharpe Ratio'].idxmax()]

# Return the Min Volatility from the run.
min_volatility = simulations_df.loc[simulations_df['Volatility'].idxmin()]

# print("PORTFOLIO TO BUY: ")
stocks_and_weights = zip(price_data_frame,max_sharpe_ratio['Portfolio Weights'])
portfolio_to_buy = dict(stocks_and_weights)
# for key, value in portfolio_to_buy.items():
#     print(key, value)
    
# init portfolio
portfolio = portfolio(data, symbols, portfolio_to_buy, strategy_name, risk_free_rate, num_periods, start_balance, months_rebalance,benchmark, start_date_strategy, end_date_strategy, interval, buy_monthly)

# execute strategy
month = 0
months_index = 1
for index, row in portfolio.stock_data.iterrows():
    if month > 0:
        portfolio.buy_stocks(index, month)
    portfolio.update_balance(index, month)
    portfolio.update_buy_and_hold(index)
    if months_index >= portfolio.months_rebalance:
        portfolio.rebalance(index, month)
        months_index = 0
    month = month + 1
    months_index = months_index + 1

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(portfolio.stock_data)

# evaluate strategy
portfolio.evaluate()
print(portfolio.result)
print("Training period: ", start_date_train, " - ", end_date_train)
print("Prediction period: ", start_date_strategy, " - ", end_date_strategy)
print("Portfolio: ", portfolio_to_buy)

plt.figure(figsize=(8,5))
plt.plot(portfolio.stock_data[portfolio.strategy_name], label=portfolio.strategy_name)
plt.plot(portfolio.stock_data['BuyAndHold'], label='BuyAndHold S&P500')
plt.title('Portfolio vs S&P500 buy and hold')
plt.ylabel('USD value portfolio')
plt.legend()
plt.show()