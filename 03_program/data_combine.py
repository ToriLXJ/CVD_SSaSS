import os
import pandas as pd
from itertools import product

def process_summary_data(folder_path, input_base_path):

    data_list = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            parts = filename.split('_')
            year = parts[1]
            gender = parts[2]
            strategy = parts[3].replace('.csv', '')

            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)

            df['Year'] = year
            df['Gender'] = gender
            df['Strategy'] = strategy

            data_list.append(df)

    data_all = pd.concat(data_list, ignore_index=True)

    col_names = ['Variable', 'Mean', 'Standard Deviation', '95% CI Lower', '95% CI Upper', 'Year', 'Gender', 'Strategy']
    data_t = data_all[col_names]


    data_stats = []

    years = ['10 years', '20 years', '30 years', '40 years', 'lifetime']
    genders = ['female', 'male', 'both']
    strategies = ['Base', 'Intervention']

    combinations = product(years, genders, strategies)

    for year, gender, strategy in combinations:
        input_file_path = f'{input_base_path}/{year}/{gender}/{strategy}_statistics.xlsx'

        if os.path.exists(input_file_path):
            df = pd.read_excel(input_file_path, skiprows=2)

            df['Year'] = year
            df['Gender'] = gender
            df['Strategy'] = strategy

            data_stats.append(df)

    data_stats = pd.concat(data_stats, ignore_index=True)
    data_stats = data_stats.drop_duplicates()
    data_stats.dropna(how='all', inplace=True)


    col_names = ['Statistic', 'Cost', 'QALY', 'Year', 'Gender', 'Strategy']
    data_s = data_stats[col_names]
    data_s = data_s.rename(columns={'Statistic': 'Variable'})
    data_s = data_s[data_s['Variable'].isin(['Mean', 'Std Deviation', '95% Lower Bound', '95% Upper Bound'])]


    data_pivot = data_s.pivot_table(index=['Year', 'Gender', 'Strategy'], columns='Variable', values=['Cost', 'QALY']).reset_index()
    data_pivot.columns = [' '.join(col).strip() for col in data_pivot.columns.values]

    return data_t, data_pivot