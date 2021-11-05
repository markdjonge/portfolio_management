import pandas as pd
import pandas_datareader as web
import csv

# set query
start_date = '2011-01-01'
interval = 'm '

# load tickers from csv
tickers = pd.read_csv(r'./tickers.csv')

# get stock returns
stock_returns = pd.DataFrame()

for c in tickers.values:
    try:
        data = web.get_data_yahoo(c[0], '1999-01-01', interval = 'm')
        stock_returns[c[0]] = data['Adj Close']
    except:
        pass
    finally:
        pass

# Save returns to excel sheet
stock_returns.to_excel("output22.xlsx")
