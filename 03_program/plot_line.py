import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def plot_data(ax, gender, variable, strategy, data_t, population, 
            mean_col, lower_col, upper_col, marker, color, linestyle, variable_map, legends):
    data_filtered = data_t[(data_t['Variable'] == variable) & 
                           (data_t['Gender'] == gender) & 
                           (data_t['Strategy'] == strategy)]
    
    mean_value = data_filtered[mean_col] * population[gender] / 1_000_000
    lower_value = data_filtered[lower_col] * population[gender] / 1_000_000
    upper_value = data_filtered[upper_col] * population[gender] / 1_000_000
    
    yerr = [
        mean_value - lower_value,
        upper_value - mean_value
    ]
    
    ax.errorbar(data_filtered['Year'], mean_value, 
                yerr=yerr, fmt=marker, capsize=5, color=color)

    line = ax.plot(data_filtered['Year'], mean_value, color=color, 
                   marker=marker, markerfacecolor='white', markeredgewidth=2, linestyle=linestyle)[0]

    if (strategy, variable) not in legends:
        legends.add((strategy, variable))
        return line, f'{strategy} {variable_map[variable]}'
    
    return line, None

def sort_key(label):
    if 'Intervention' in label:
        if 'ischemic' in label:
            return (0, label)
        else:
            return (1, label)
    elif 'Base' in label:
        if 'ischemic' in label:
            return (2, label)
        else:
            return (3, label)
    else:
        return (4, label)


def create_summary_plot(data_t, population, colors, markers, linestyles, pdf_path):
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['font.size'] = 18

    event_variables = ['t_IS_event', 't_HS_event', 't_US_event']
    death_variables = ['t_IS_death', 't_HS_death', 't_US_death']
    chd_event_variables = ['t_chd_event']
    chd_death_variables = ['t_chd_death']
    strategies = ['Base', 'Intervention']

    variable_map = { 
        't_IS_event': 'ischemic stroke events',
        't_HS_event': 'hemorrhagic stroke events',
        't_US_event': 'undetermined stroke events',
        't_IS_death': 'ischemic stroke deaths',
        't_HS_death': 'hemorrhagic stroke deaths',
        't_US_death': 'undetermined stroke deaths',
        't_chd_event': 'CHD events',
        't_chd_death': 'CHD deaths'
    }

    num_rows = 4
    num_cols = 3
    fig, axs = plt.subplots(num_rows, num_cols, figsize=(18, 18), dpi=200, sharey='row')
    fig.subplots_adjust(wspace=0.5, hspace=0.5)

    genders = ['both', 'female', 'male']
    subplot_labels = [chr(65+i) for i in range(num_rows * num_cols)]

    label_index = 0

    for i in range(4):
        for j, gender in enumerate(genders):
            if i == 0:
                variables_to_plot = event_variables  # Stroke events (first row)
            elif i == 1:
                variables_to_plot = death_variables  # Stroke deaths (second row)
            elif i == 2:
                variables_to_plot = chd_event_variables  # CHD events (third row)
            else:
                variables_to_plot = chd_death_variables  # CHD deaths (fourth row)
            
            ax = axs[i, j]

            legends = set()
            legend_handles = []
            legend_labels = []
            
            for variable, strategy in zip(variables_to_plot * 2, strategies * len(variables_to_plot)):
                marker = markers[strategies.index(strategy)]
                linestyle = linestyles[strategies.index(strategy)]
                color = colors[(variables_to_plot.index(variable) + 
                                strategies.index(strategy) * len(variables_to_plot)) % len(colors)]

                if variable in ['t_chd_event', 't_chd_death']:
                    color = colors[0] if strategy == 'Base' else colors[3]

                line, label = plot_data(ax, gender, variable, strategy, data_t, population, 'Mean', '95% CI Lower', 
                                '95% CI Upper', marker, color, linestyle, variable_map, legends)
                
                if label:
                    legend_handles.append(line)
                    legend_labels.append(label)

            titles = [
                "stroke events",
                "stroke deaths",
                "CHD events",
                "CHD deaths"
            ]

            ax.set_title(f'{gender.capitalize()} {titles[i]}', fontsize=18, loc='center')

            if i == 3:
                ax.set_xlabel('Year', fontsize=16)
            
            if j == 0:
                ax.set_ylabel('Number of events (in millions)' if i in [0, 2] else 'Number of deaths (in millions)', 
                                fontsize=16)
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            ax.text(-0.03, 1.07, subplot_labels[label_index], transform=ax.transAxes, fontsize=18, fontweight='bold',
                     va='top', ha='right')
            label_index += 1

            if j == 2:
                sorted_handles_labels = sorted(zip(legend_handles, legend_labels), key=lambda x: sort_key(x[1]))
                sorted_handles, sorted_labels = zip(*sorted_handles_labels)
                ax.legend(sorted_handles, sorted_labels, loc='upper left', bbox_to_anchor=(1, 1), fontsize=14)

    plt.tight_layout()
    plt.savefig(pdf_path, format='pdf')
    plt.show()
