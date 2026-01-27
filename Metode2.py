
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import csv
import row


data = pd.read_csv('Forbruk_NO1_NO5.csv')

price_NO1 = pd.read_csv('NO1_prices.csv')
price_NO5 = pd.read_csv('NO5_prices.csv')

Temp_Bergen = pd.read_csv('Temp_Bergen.csv')
Temp_Oslo = pd.read_csv('Temp_Oslo.csv')

def metode2(data, price_area, price_NO1, price_N05, Temp_Bergen, Temp_Oslo):

    # Filterer for dato:
    start_date1 = '2024-10-01'
    end_date1 = '2024-12-31'

    start_date2 = '2025-10-01'
    end_date2 = '2025-12-31'

    # Demand:

    data_demand = data[data['price_area'] == price_area].copy()
    data_demand['Date'] = pd.to_datetime(data_demand['Date'])
    data_demand['Hour'] = data_demand['Hour'].astype(int)

    data_demand_filtered1 = data_demand[ (data_demand['Date'] >= start_date1) &
                                       (data_demand['Date'] <= end_date1)].copy()

    data_demand_filtered2 = data_demand[(data_demand['Date'] >= start_date2) &
                                        (data_demand['Date'] <= end_date2)].copy()







