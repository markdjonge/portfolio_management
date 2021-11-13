import pandas_datareader as web
import numpy as np

class portfolio:
    def __init__(self, data, symbols, stocks_and_weights, strategy_name,risk_free_rate, num_periods, start_balance, months_rebalance, benchmark, start_date_strategy, end_date_strategy, interval, buy_monthly):
        self.strategy_name = strategy_name
        self.start_balance = start_balance
        self.buy_monthly = buy_monthly
        self.start_date_strategy = start_date_strategy
        self.end_date_strategy = end_date_strategy
        self.interval = interval
        self.benchmark = benchmark
        self.data = data
        self.current_balance = 0
        self.stocks = symbols
        self.benchmark_stocks = 0
        self.stock_data = {}
        self.risk_free_rate = risk_free_rate
        self.num_periods = num_periods
        self.months_rebalance = months_rebalance
        self.portfolio = stocks_and_weights
        self.portfolio_stocks = {}
        self.set_portfolio()

    def set_portfolio(self):
        self.stock_data = self.data.loc[self.start_date_strategy:self.end_date_strategy]
        self.stock_data['benchmark'] = web.get_data_yahoo(self.benchmark, self.start_date_strategy, self.end_date_strategy, interval = self.interval)['Adj Close']
        self.benchmark_stocks = self.start_balance / self.stock_data['benchmark'][0]
        for item in self.portfolio.items():
            start_price = self.stock_data[item[0]][0]
            # print("start price: ", start_price)
            self.portfolio_stocks[item[0]] = self.start_balance * item[1] / start_price
            # print("Number of stocks purchased: ", self.portfolio_stocks[item[0]])

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
        
    def buy_stocks(self, index, month):
        self.update_balance(index, month)
        for item in self.portfolio.items():
            stock_price = self.stock_data[item[0]][index]
            # print("stock price: ", stock_price)
            self.portfolio_stocks[item[0]] = self.portfolio_stocks[item[0]] + (self.buy_monthly * item[1] / stock_price)
            # print("Number of stocks purchased: ", self.portfolio_stocks[item[0]])
            
        
    
    def update_buy_and_hold(self, index):
        bench = self.stock_data.loc[[index],['benchmark']]
        stocks = self.benchmark_stocks
        self.stock_data.loc[[index], ['BuyAndHold']] = bench.benchmark * stocks

    def evaluate(self):
        self.stock_data['return'] = self.stock_data[self.strategy_name].pct_change()*100
        self.mean = np.mean(self.stock_data['return']) * self.num_periods
        self.sdev = np.std(self.stock_data['return']) * np.sqrt(self.num_periods)
        self.sharpe = (self.mean - self.risk_free_rate) / self.sdev
        self.result = "mean: " , self.mean, " sdev: ", self.sdev, " sharpe: ", self.sharpe