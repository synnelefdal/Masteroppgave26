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


print('Prosent endring i NO1:',(f"{Difference_in_Difference(data,'NO1'):.3f}"), '\n', '\n')

print('Prosent endring i NO5:',(f"{Difference_in_Difference(data,'NO5'):.3f}"), '\n', '\n')

'''def total_forbruk_per_malepunkt(data):
    return (data['quantity_kwh'] / data['metering_point_count']).sum()

def Difference_in_Difference2(dataset, treatment_area, control_area):

    # Perioder
    start_date1 = '2024-10-01'
    end_date1   = '2024-12-31'

    start_date2 = '2025-10-01'
    end_date2   = '2025-12-31'

    dataset = dataset.copy()
    dataset['Date'] = pd.to_datetime(dataset['Date'])
    dataset['Hour'] = dataset['Hour'].astype(int)

    # -------------------------
    # TREATMENT AREA
    # -------------------------
    treat = dataset[dataset['price_area'] == treatment_area]

    treat_before = treat[(treat['Date'] >= start_date1) & (treat['Date'] <= end_date1)]
    treat_after  = treat[(treat['Date'] >= start_date2) & (treat['Date'] <= end_date2)]

    forbruk_treat_before = total_forbruk_per_malepunkt(treat_before)
    forbruk_treat_after  = total_forbruk_per_malepunkt(treat_after)

    # -------------------------
    # CONTROL AREA
    # -------------------------
    control = dataset[dataset['price_area'] == control_area]

    control_before = control[(control['Date'] >= start_date1) & (control['Date'] <= end_date1)]
    control_after  = control[(control['Date'] >= start_date2) & (control['Date'] <= end_date2)]

    forbruk_control_before = total_forbruk_per_malepunkt(control_before)
    forbruk_control_after  = total_forbruk_per_malepunkt(control_after)

    # -------------------------
    # DIFFERENCE-IN-DIFFERENCE
    # -------------------------
    change_treat = (forbruk_treat_after - forbruk_treat_before) / forbruk_treat_before
    change_control = (forbruk_control_after - forbruk_control_before) / forbruk_control_before

    DiD = change_treat - change_control

    return {
        "Treatment change": change_treat,
        "Control change": change_control,
        "DiD": DiD
    }

resultat = Difference_in_Difference2(
    dataset=data,
    treatment_area="NO1",
    control_area="NO1"
)

print(resultat)'''