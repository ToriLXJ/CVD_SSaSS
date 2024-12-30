import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

def create_tornado_diagram(tornado_data, output_pdf_path, base_case_icer):
    cols = ['Variable Description', 'Variable Low', 'Variable High', 'Impact', 'Low', 'High']
    data = tornado_data[cols].copy()

    data.loc[data['Variable Description'] == 'Discount rate (%)', 'Variable Low'] = data[data['Variable Description'] 
        == 'Discount rate (%)']['Variable Low'].map(lambda y: '{:.0%}'.format(y))
    data.loc[data['Variable Description'] == 'Discount rate (%)', 'Variable High'] = data[data['Variable Description'] 
        == 'Discount rate (%)']['Variable High'].map(lambda y: '{:.0%}'.format(y))
    data['ranges'] = data['High'] - data['Low']
    data_sorted = data.sort_values(by='ranges', ascending=True)

    plt.rcParams['font.family'] = 'Times New Roman'
    fig, ax = plt.subplots(figsize=(20, 10), dpi=200)

    bar_height = 0.5

    for i, (index, row) in enumerate(data_sorted.iterrows()):
        param = row['Variable Description']
        low = row['Low']
        high = row['High']
        v_low = row['Variable Low']
        v_high = row['Variable High']
        impact = row['Impact']

        len_v_low = len(str(v_low))
        text_offset = 150 if len_v_low <= 4 else 220

        if low < base_case_icer and high > base_case_icer:
            if impact == 'Increase':
                ax.barh(param, base_case_icer - low, left=low, color='skyblue', edgecolor='grey', height=bar_height)
                ax.barh(param, high - base_case_icer, left=base_case_icer, color='salmon', edgecolor='grey', height=bar_height)
                ax.text(low - text_offset, i, f'{v_low}', ha='center', va='center', fontsize=22, color='black', backgroundcolor='white')
                ax.text(high + text_offset, i, f'{v_high}', ha='center', va='center', fontsize=22, color='black', backgroundcolor='white')
            else:
                ax.barh(param, base_case_icer - low, left=low, color='salmon', edgecolor='grey', height=bar_height)
                ax.barh(param, high - base_case_icer, left=base_case_icer, color='skyblue', edgecolor='grey', height=bar_height)
                ax.text(low - text_offset, i, f'{v_high}', ha='center', va='center', fontsize=22, color='black', backgroundcolor='white')
                ax.text(high + text_offset, i, f'{v_low}', ha='center', va='center', fontsize=22, color='black', backgroundcolor='white')
        elif high <= base_case_icer:
            ax.barh(param, high - low, left=low, color='skyblue', edgecolor='grey', height=bar_height)
        else:
            ax.barh(param, high - low, left=low, color='salmon', edgecolor='grey', height=bar_height)

    plt.axvline(base_case_icer, color='black', linestyle='-', linewidth=2, label=f'Base-case ICER: {base_case_icer}')

    x_min = data['Low'].min() - 500
    x_max = data['High'].max() + 500
    ax.set_xlim(x_min, x_max)
    ax.tick_params(axis='x', labelsize=24)
    ax.tick_params(axis='y', labelsize=24)

    ax.spines['bottom'].set_visible(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(axis='y', which='both', left=False, right=False, labelleft=False, labelright=True)

    # ax.set_xlabel('ICER ($/QALYs)', fontsize=24)
    ax.text(base_case_icer, -1.5, 'ICER ($/QALYs)', fontsize=24, ha='center', va='center')

    skyblue_patch = mpatches.Patch(color='skyblue', label='Lower variable value')
    salmon_patch = mpatches.Patch(color='salmon', label='Higher variable value')
    base_case_line = Line2D([0], [0], color='black', linewidth=2, linestyle='-', label=f'Base-case ICER: {base_case_icer}')
    plt.legend(handles=[skyblue_patch, salmon_patch, base_case_line], loc='lower left', fontsize=24)

    plt.tight_layout()
    plt.savefig(output_pdf_path, format='pdf')
    plt.show()
