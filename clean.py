import pandas as pd
import pandas_datareader as web
import csv

df = pd.read_excel(io='output.xlsx', sheet_name="Sheet1")
# print(df.head(5))
for c in df:
    if df[c].count() != 96:
        print("Deleting ETF: ",  df[c])
        df.drop(c, 1, inplace=True)

df.to_excel("cleaned.xlsx")