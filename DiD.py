# Difference in Difference

import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import csv
import row
#from sympy.benchmarks.bench_discrete_log import data_set_1

data = pd.read_csv('Forbruk_NO1_NO5.csv')


def Difference_in_Difference(dataset, price_area):
    # filterer for dato
    start_date1 = '2024-10-01'
    end_date1   = '2024-12-31'

    start_date2 = '2025-10-01'
    end_date2   = '2025-12-31'


    #filtere for prissone
    dataset_updated_area = dataset[dataset['price_area'] == price_area].copy()
    dataset_updated_area['Date'] = pd.to_datetime(dataset_updated_area['Date'])
    dataset_updated_area['Hour'] = dataset_updated_area['Hour'].astype(int)

    # filterer for dato videre

    #for første året
    data_set_1 = dataset_updated_area[(dataset_updated_area['Date'] >= start_date1) & (dataset_updated_area['Date'] <= end_date1)]
    data_set_1 = data_set_1.copy()


    #for andre året
    data_set_2 = dataset_updated_area[(dataset_updated_area['Date'] >= start_date2) & (dataset_updated_area['Date'] <= end_date2)]
    data_set_2 = data_set_2.copy()


    #Finne totalt forbruk over valgt tid for hvert målepunkt år 1

    forbruk1 = 0

    for index, rad in data_set_1.iterrows():
        forbruk1 += rad['quantity_kwh'] / rad['metering_point_count']
        #print(forbruk1)

    print(price_area ,'forbruk år 1:',forbruk1)


    # Finne totalt forbruk over valgt tid for hvert målepunkt år 2

    forbruk2 = 0

    for index, rad in data_set_2.iterrows():
        forbruk2 += rad['quantity_kwh'] / rad['metering_point_count']
        # print(forbruk2)

    print(price_area ,'forbruk år 2:', forbruk2)


    #Finne forskjell DiD

    DiD = ((forbruk2-forbruk1) / forbruk1 ) * 100

    return DiD


print('Prosent endring i NO1:',Difference_in_Difference(data,'NO1'), '\n')

print('Prosent endring i NO5:',Difference_in_Difference(data,'NO5'), '\n')
