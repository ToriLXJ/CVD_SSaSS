import os
import pandas as pd
import numpy as np
import scipy.stats as stats
from itertools import product
from statsmodels.stats.proportion import proportion_confint

def compute_and_append_stats(data, ci_func, summary_dict):
    for column in data.columns:
        if column not in summary_dict['Variable']:
            stats_dict = compute_stats(data[column], ci_func=ci_func)
            summary_dict['Variable'].append(column)
            summary_dict['Mean'].append(stats_dict['mean'])
            summary_dict['Standard Deviation'].append(stats_dict['std'])
            summary_dict['95% CI Lower'].append(stats_dict['95% CI Lower'])
            summary_dict['95% CI Upper'].append(stats_dict['95% CI Upper'])
            summary_dict['2.5%'].append(stats_dict['2.5%'])
            summary_dict['10%'].append(stats_dict['10%'])
            summary_dict['Median'].append(stats_dict['median'])
            summary_dict['90%'].append(stats_dict['90%'])
            summary_dict['97.5%'].append(stats_dict['97.5%'])
            summary_dict['Min'].append(stats_dict['min'])
            summary_dict['Max'].append(stats_dict['max'])

def compute_stats(data, ci_func=None, alpha=0.05):
    mean = data.mean()
    min_val = data.min()
    q025 = data.quantile(0.025)
    q10 = data.quantile(0.1)
    median = data.median()
    q90 = data.quantile(0.9)
    q975 = data.quantile(0.975)
    max_val = data.max()
    std = data.std()

    if ci_func:
        ci_lower, ci_upper = ci_func(data, alpha=alpha)
    else:
        ci_lower, ci_upper = None, None

    return {
        'mean': mean,
        'std': std,
        'min': min_val,
        '2.5%': q025,
        '10%': q10,
        'median': median,
        '90%': q90,
        '97.5%': q975,
        'max': max_val,
        '95% CI Lower': ci_lower,
        '95% CI Upper': ci_upper
    }

def normal_ci(data, alpha=0.05):
    mean = np.mean(data)
    std = np.std(data, ddof=1)
    n = len(data)
    stderr = std / np.sqrt(n)
    z = stats.norm.ppf(1 - alpha / 2)
    ci_lower = mean - z * stderr
    ci_upper = mean + z * stderr
    return ci_lower, ci_upper

def compute_wilson_ci(data, alpha=0.05):
    data = data.dropna()
    if len(data) == 0 or data.sum() == 0:
        return np.nan, np.nan
    successes = data.sum()
    nobs = len(data)
    ci_lower, ci_upper = proportion_confint(successes, nobs, alpha=alpha, method='wilson')
    return ci_lower, ci_upper


def bootstrap_ci(data, alpha=0.05, n_bootstrap=10000):
    n = len(data)
    bootstrap_means = np.zeros(n_bootstrap)
    for i in range(n_bootstrap):
        bootstrap_sample = np.random.choice(data, size=n, replace=True)
        bootstrap_means[i] = np.mean(bootstrap_sample)
    ci_lower = np.percentile(bootstrap_means, 100 * alpha / 2)
    ci_upper = np.percentile(bootstrap_means, 100 * (1 - alpha / 2))
    return ci_lower, ci_upper

def process_data(input_file_path_alldata, summary_dict, gender, strategy, year):
    summary_dict = {
        'Variable': [],
        'Mean': [],
        'Standard Deviation': [],
        '95% CI Lower': [],
        '95% CI Upper': [],
        '2.5%': [],
        '10%': [],
        'Median': [],
        '90%': [],
        '97.5%': [],
        'Min': [],
        'Max': []
    }

    year_mapping = {
        '10 years': 10,
        '20 years': 20,
        '30 years': 30,
        '40 years': 40,
        'lifetime': 100
    }

    df = pd.read_excel(input_file_path_alldata, skiprows=2)
    df_cleaned = df.dropna(subset=['t_stroke_deathage', 't_chd_deathage', 't_noncvd_deathage', 't_initial_age',
                                   't_stroke_death', 't_chd_death', 't_noncvd_death', 
                                   't_stroke_event', 't_chd_event', 'distStrokeType',
                                   'Cost', 'QALY'])


    df_cleaned['t_deathage'] = df_cleaned[['t_stroke_deathage', 't_chd_deathage', 't_noncvd_deathage']].max(axis=1, skipna=True)
    year_int = year_mapping[year]
    df_cleaned['t_timeperiod'] = np.where(
        df_cleaned['t_deathage'] - df_cleaned['t_initial_age'] < 0,
        year_int,
        df_cleaned['t_deathage'] - df_cleaned['t_initial_age']
    )
    
    value_counts = df_cleaned['distStrokeType'].value_counts()
    value_percentages = value_counts / value_counts.sum()
    IS_ratio = value_percentages[1]
    HS_ratio = value_percentages[2]
    US_ratio = value_percentages[3]

    df_cleaned['t_IS_event'] = df_cleaned['t_stroke_event'] * IS_ratio
    df_cleaned['t_HS_event'] = df_cleaned['t_stroke_event'] * HS_ratio
    df_cleaned['t_US_event'] = df_cleaned['t_stroke_event'] * US_ratio
    df_cleaned['t_IS_death'] = df_cleaned['t_stroke_death'] * IS_ratio
    df_cleaned['t_HS_death'] = df_cleaned['t_stroke_death'] * HS_ratio
    df_cleaned['t_US_death'] = df_cleaned['t_stroke_death'] * US_ratio

    df_cleaned['t_stroke_event_annual'] = df_cleaned['t_stroke_event'] / df_cleaned['t_timeperiod']
    df_cleaned['t_stroke_death_annual'] = df_cleaned['t_stroke_death'] / df_cleaned['t_timeperiod']
    df_cleaned['t_IS_event_annual'] = df_cleaned['t_IS_event'] / df_cleaned['t_timeperiod']
    df_cleaned['t_HS_event_annual'] = df_cleaned['t_HS_event'] / df_cleaned['t_timeperiod']
    df_cleaned['t_US_event_annual'] = df_cleaned['t_US_event'] / df_cleaned['t_timeperiod']
    df_cleaned['t_IS_death_annual'] = df_cleaned['t_IS_death'] / df_cleaned['t_timeperiod']
    df_cleaned['t_HS_death_annual'] = df_cleaned['t_HS_death'] / df_cleaned['t_timeperiod']
    df_cleaned['t_US_death_annual'] = df_cleaned['t_US_death'] / df_cleaned['t_timeperiod']
    df_cleaned['t_chd_event_annual'] = df_cleaned['t_chd_event'] / df_cleaned['t_timeperiod']
    df_cleaned['t_chd_death_annual'] = df_cleaned['t_chd_death'] / df_cleaned['t_timeperiod']
    df_cleaned['t_noncvd_death_annual'] = df_cleaned['t_noncvd_death'] / df_cleaned['t_timeperiod']
    df_cleaned['t_Cost_annual'] = df_cleaned['Cost'] / df_cleaned['t_timeperiod']
    df_cleaned['t_QALY_annual'] = df_cleaned['QALY'] / df_cleaned['t_timeperiod']


    data_death = df_cleaned[['t_stroke_death', 't_IS_death', 't_HS_death', 't_US_death', 't_chd_death', 't_noncvd_death']].copy()
    compute_and_append_stats(data_death, compute_wilson_ci, summary_dict)

    data_event = df_cleaned[['t_stroke_event', 't_IS_event', 't_HS_event', 't_US_event', 't_chd_event']].copy()
    compute_and_append_stats(data_event, bootstrap_ci, summary_dict)

    data_cost = df_cleaned[['Cost', 'QALY']].copy()
    compute_and_append_stats(data_cost, normal_ci, summary_dict)

    data_death_annual = df_cleaned[['t_stroke_death_annual', 't_IS_death_annual', 't_HS_death_annual', 't_US_death_annual', 
                                't_chd_death_annual', 't_noncvd_death_annual']].copy()
    compute_and_append_stats(data_death_annual, compute_wilson_ci, summary_dict)

    data_event_annual = df_cleaned[['t_stroke_event_annual', 't_IS_event_annual', 't_HS_event_annual', 't_US_event_annual', 
                                't_chd_event_annual']].copy()
    compute_and_append_stats(data_event_annual, bootstrap_ci, summary_dict)

    data_cost_annual = df_cleaned[['t_Cost_annual', 't_QALY_annual']].copy()
    compute_and_append_stats(data_cost_annual, normal_ci, summary_dict)

    data_age = df_cleaned[['t_stroke_deathage', 't_chd_deathage', 't_noncvd_deathage', 't_deathage', 't_timeperiod']].copy()


    for column in data_age.columns:
        data_age_filtered = data_age[data_age[column] != 0]
        data_age_filtered = data_age_filtered[[column]]
        compute_and_append_stats(data_age_filtered, normal_ci, summary_dict)


    # print(f"The statistics of {gender} in {strategy} during {year}.")

    return summary_dict


