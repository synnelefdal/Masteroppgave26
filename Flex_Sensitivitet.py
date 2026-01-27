
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

def flex_sensitivitet(data, price_area, Temp_Bergen, Temp_Oslo, price_NO1, price_NO5):
    # ------------------- Filterer for dato ---------- #
    start_date1 = '2024-10-01'
    end_date1 = '2024-12-31'

    start_date2 = '2025-10-01'
    end_date2 = '2025-12-31'

    # ----------------- Demand ------------------ #

    data_demand = data[data['price_area'] == price_area].copy()
    data_demand['Date'] = pd.to_datetime(data_demand['Date'])
    data_demand['Hour'] = data_demand['Hour'].astype(int)

    data_demand_filtered1 = data_demand[(data_demand['Date'] >= start_date1) &
                                        (data_demand['Date'] <= end_date1)].copy()

    data_demand_filtered2 = data_demand[(data_demand['Date'] >= start_date2) &
                                        (data_demand['Date'] <= end_date2)].copy()

    for index, rad in data_demand_filtered1.iterrows():
        data_demand_filtered1.loc[index, 'kWh/Metering_point'] = rad['quantity_kwh'] / rad['metering_point_count']

    for index, rad in data_demand_filtered2.iterrows():
        data_demand_filtered2.loc[index, 'kWh/Metering_point'] = rad['quantity_kwh'] / rad['metering_point_count']

    total_hour1 = data_demand_filtered1.groupby(['Date', 'Hour'])['kWh/Metering_point'].sum().reset_index()
    total_hour2 = data_demand_filtered2.groupby(['Date', 'Hour'])['kWh/Metering_point'].sum().reset_index()
