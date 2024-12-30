
import pandas as pd
import numpy as np
from itertools import product

def format_number(value):
    sign = 1 if value >= 0 else -1
    abs_value = abs(value)

    if abs_value >= 1e9:
        return sign * (abs_value / 1e9), 'billion'
    elif abs_value >= 1e6:
        return sign * (abs_value / 1e6), 'million'
    elif abs_value >= 1e3:
        return sign * (abs_value / 1e3), 'thousand'
    return value, ''

def unify_units(base_value, intervention_value, base_unit, intervention_unit):
    scales = {
        'billion': 1e9,
        'million': 1e6,
        'thousand': 1e3,
        '': 1
    }

    if base_unit == intervention_unit:
        return base_value, intervention_value, base_unit, intervention_unit

    base_scale = scales[base_unit]
    int_scale = scales[intervention_unit]

    if base_scale > int_scale:
        base_value = base_value * (base_scale / int_scale)
        base_unit = intervention_unit
    else:
        intervention_value = intervention_value * (int_scale / base_scale)
        intervention_unit = base_unit

    return base_value, intervention_value, base_unit, intervention_unit

def convert_to_same_unit(base_value, intervention_value):
    if base_value == 0 or intervention_value == 0:
        return base_value, intervention_value, '', ''

    base_value, base_unit = format_number(base_value)
    intervention_value, intervention_unit = format_number(intervention_value)
    base_value, intervention_value, base_unit, intervention_unit = unify_units(base_value, intervention_value, base_unit, intervention_unit)
    return base_value, intervention_value, base_unit, intervention_unit

def calculate_variable(data, population, year, gender, variable, strategy):
    subset = data[(data['Year'] == year) & (data['Gender'] == gender) & 
                  (data['Strategy'] == strategy) & (data['Variable'] == variable)]
    
    if variable.endswith('age'):
        mean = subset['Mean'].sum()
        ci_lower = subset['95% CI Lower'].sum()
        ci_upper = subset['95% CI Upper'].sum()
    else:
        mean = (subset['Mean'] * population[gender]).sum()
        ci_lower = (subset['95% CI Lower'] * population[gender]).sum()
        ci_upper = (subset['95% CI Upper'] * population[gender]).sum()

    return mean, ci_lower, ci_upper

def calculate_all_variables(data_pivot, data_t, population, years, genders, strategies, flag_abs, flag_format):
    cache = {}
    variables = ['t_stroke_event', 't_IS_event', 't_HS_event', 't_US_event', 
                    't_stroke_death', 't_IS_death', 't_HS_death', 't_US_death',
                    't_chd_event', 't_chd_death', 'Cost', 'QALY', 't_deathage',
                    't_stroke_event_annual', 't_IS_event_annual', 't_HS_event_annual', 't_US_event_annual',
                    't_stroke_death_annual', 't_IS_death_annual', 't_HS_death_annual', 't_US_death_annual',
                    't_chd_event_annual', 't_chd_death_annual', 't_noncvd_death_annual', 't_Cost_annual', 't_QALY_annual']
    def get_values(year, gender, variable, strategy):
        if (year, gender, variable, strategy) not in cache:
            cache[(year, gender, variable, strategy)] = calculate_variable(data_t, population, year, gender, variable, strategy)
        return cache[(year, gender, variable, strategy)]

    results = []
    df_plot_data = []

    for year, gender, variable in product(years, genders, variables):
        base_mean, base_ci_lower, base_ci_upper = get_values(year, gender, variable, 'Base')
        intervention_mean, intervention_ci_lower, intervention_ci_upper = get_values(year, gender, variable, 'Intervention')


        mean_diff = intervention_mean - base_mean
        ci_lower_diff = intervention_ci_lower - base_ci_lower
        ci_upper_diff = intervention_ci_upper - base_ci_upper


        change_mean = abs(mean_diff) if flag_abs else mean_diff

        is_age_var = variable.endswith('age')
        if is_age_var:
            if flag_abs:
                change_ci_lower = min(abs(ci_lower_diff), abs(-ci_upper_diff))
                change_ci_upper = max(abs(ci_lower_diff), abs(-ci_upper_diff))
            else:
                change_ci_lower = min(ci_lower_diff, -ci_upper_diff)
                change_ci_upper = max(ci_lower_diff, -ci_upper_diff)
        else:
            if flag_abs:
                change_ci_lower = abs(ci_lower_diff)
                change_ci_upper = abs(ci_upper_diff)
            else:
                change_ci_lower = ci_lower_diff
                change_ci_upper = ci_upper_diff

        if flag_format:
            base_val_converted, intervention_val_converted, base_unit, intervention_unit = convert_to_same_unit(base_mean, intervention_mean)
            unit_scale = {
                'billion': 1e9,
                'million': 1e6,
                'thousand': 1e3,
                '': 1
            }
            scale_factor = unit_scale[base_unit]

            base_ci_lower_converted = base_ci_lower / scale_factor
            base_ci_upper_converted = base_ci_upper / scale_factor
            intervention_ci_lower_converted = intervention_ci_lower / scale_factor
            intervention_ci_upper_converted = intervention_ci_upper / scale_factor

            change_mean_converted = change_mean / scale_factor
            change_ci_lower_converted = change_ci_lower / scale_factor
            change_ci_upper_converted = change_ci_upper / scale_factor

            base_combined = f"{round(base_val_converted, 2)} ({round(base_ci_lower_converted, 2)}, {round(base_ci_upper_converted, 2)})"
            intervention_combined = f"{round(intervention_val_converted, 2)} ({round(intervention_ci_lower_converted, 2)}, {round(intervention_ci_upper_converted, 2)})"
            change_combined = f"{round(change_mean_converted, 2)} ({round(change_ci_lower_converted, 2)}, {round(change_ci_upper_converted, 2)})"

            change_unit = base_unit

            df_plot_data.append({
                'Year': year,
                'Gender': gender,
                'Variable': variable,
                'Change_mean': change_mean_converted,
                'Change_ci_lower': change_ci_lower_converted,
                'Change_ci_upper': change_ci_upper_converted,
                'Change_unit': change_unit
            })

            results.append({
                'Year': year,
                'Gender': gender,
                'Variable': variable,
                'Base': base_combined,
                'Intervention': intervention_combined,
                'Change': change_combined,
                'Base Unit': base_unit,
                'Intervention Unit': base_unit,
                'Change Unit': base_unit
            })
        else:
            base_combined = f"{round(base_mean, 2)} ({round(base_ci_lower, 2)}, {round(base_ci_upper, 2)})"
            intervention_combined = f"{round(intervention_mean, 2)} ({round(intervention_ci_lower, 2)}, {round(intervention_ci_upper, 2)})"
            change_combined = f"{round(change_mean, 2)} ({round(change_ci_lower, 2)}, {round(change_ci_upper, 2)})"

            df_plot_data.append({
                'Year': year,
                'Gender': gender,
                'Variable': variable,
                'Change_mean': change_mean,
                'Change_ci_lower': change_ci_lower,
                'Change_ci_upper': change_ci_upper,
                'Change_unit': ''
            })

            results.append({
                'Year': year,
                'Gender': gender,
                'Variable': variable,
                'Base': base_combined,
                'Intervention': intervention_combined,
                'Change': change_combined,
                'Base Unit': '',
                'Intervention Unit': '',
                'Change Unit': ''
            })

    return pd.DataFrame(results), pd.DataFrame(df_plot_data)

