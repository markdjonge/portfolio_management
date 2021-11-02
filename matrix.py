import pandas as pd
import pandas_datareader as web
import csv
import numpy as np

df = pd.read_excel(io='cleaned.xlsx', sheet_name="Sheet1")

# print(df.head())
corrMatrix = df.corr()
# print(corrMatrix)

corr_list = corrMatrix.tolist()
print(corr_list)