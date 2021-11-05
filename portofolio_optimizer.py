import pandas as pd
import pandas_datareader as web
import csv

# load excel data into dataframe
data = pd.read_excel('./cleaned.xlsx', index_col=0)

# load assets
assets = data.columns

# optimize portfolio
