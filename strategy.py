import pandas as pd
import pandas_datareader as web
import numpy as np
from scipy.optimize import minimize

# set portofolio vars
strategy_name = "Reb. sem. yearly"
stocks = ["AAPL", "^GSPC", "GLD"]
start_date = '01/01/2015'
interval = 'm'
months_rebalance = 6
portfolio_weights = [0.70,0.15,0.15]
start_balance = 1000
risk_free_rate = 0.001
num_periods = 12

# set portfolio object
class portfolio:
    def __init__(self):
        self.strategy_name = strategy_name
        self.start_balance = start_balance
        self.current_balance = 0
        self.stocks = stocks
        self.stock_data = {}
        self.risk_free_rate = risk_free_rate
        self.num_periods = num_periods
        self.months_rebalance = months_rebalance
        self.portfolio_weights = portfolio_weights
        self.portfolio_stocks = {}
        self.portfolio = {}
        self.set_portfolio()

    def set_portfolio(self):
        stocks_and_weights = zip(self.stocks,self.portfolio_weights) 
        self.portfolio = dict(stocks_and_weights)
        self.stock_data = web.get_data_yahoo(self.stocks, start_date, interval = interval)['Adj Close']
        for item in self.portfolio.items():
            start_price = self.stock_data[item[0]][0]
            print("start price: ", start_price) 
            self.portfolio_stocks[item[0]] = self.start_balance * item[1] / start_price
            print("Number of stocks purchased: ", self.portfolio_stocks[item[0]])
    
    def get_current_balance(self, month):
        self.current_balance = 0
        for item in self.portfolio_stocks.items():
            self.current_balance = self.current_balance + self.stock_data[item[0]][month] * item[1]
            # print(self.stock_data[item[0]][day],item[1])
        return self.current_balance
        # print(self.portfolio_stocks)


    def rebalance(self, index, month):
        current_balance = self.get_current_balance(month)
        for item in self.portfolio.items():
            current_price = self.stock_data[item[0]][month]
            self.portfolio_stocks[item[0]] = current_balance * item[1] / current_price
            # self.stock_data.loc[[index], ['Actions']] = "Rebalanced"

    def update_balance(self, index, month):
        self.stock_data.loc[[index],[self.strategy_name]] = self.get_current_balance(month)
    
    def evaluate(self):
        self.stock_data['return'] = self.stock_data[self.strategy_name].pct_change()*100
        self.mean = np.mean(self.stock_data['return']) * self.num_periods
        self.sdev = np.std(self.stock_data['return']) * np.sqrt(self.num_periods)
        self.sharpe = (self.mean - self.risk_free_rate) / self.sdev
        self.result = "mean: " , self.mean, " sdev: ", self.sdev, " sharpe: ", self.sharpe
        

# init portfolio
portfolio = portfolio()

# get stock data
df = pd.DataFrame()
for ticker in stocks:
    df[ticker] = web.get_data_yahoo(ticker, start_date, interval=interval)['Adj Close']
# print("Stock data loaded: ")
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(df)

# execute strategy
month = 0
months_index = 1
for index, row in df.iterrows():
    portfolio.update_balance(index, month)
    if months_index >= portfolio.months_rebalance:
        portfolio.rebalance(index, month)
        months_index = 0
    month = month + 1
    months_index = months_index + 1

with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(portfolio.stock_data)

portfolio.evaluate()
print(portfolio.result)



   

