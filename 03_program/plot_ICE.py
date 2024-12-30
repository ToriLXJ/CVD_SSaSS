import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import matplotlib.lines as mlines
from scipy.stats import chi2

def draw_solid_confidence_ellipse(data, ax, label, color, linewidth=2):
    mean_x = data['Incr. QALY'].mean()
    mean_y = data['Incr. Cost'].mean()
    
    cov = np.cov(data['Incr. QALY'], data['Incr. Cost'])
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    order = eigenvalues.argsort()[::-1]
    eigenvalues, eigenvectors = eigenvalues[order], eigenvectors[:, order]
    
    angle = np.degrees(np.arctan2(*eigenvectors[:, 0][::-1]))
    
    confidence_level = 0.95
    p = 2
    multiplier = chi2.ppf(confidence_level, p)
    
    width, height = 2 * np.sqrt(eigenvalues * multiplier)
    
    if mean_y < 0:
        offset_x = 0.2
        offset_y = 1000
        mean_x += offset_x
        mean_y -= offset_y

    ellipse = Ellipse(xy=(mean_x, mean_y), width=width, height=height, angle=angle,
                      edgecolor=color, facecolor='none', linewidth=linewidth)
    
    ax.add_patch(ellipse)

def create_ice_plot(female_data, male_data, WTP_value, colors, output_pdf_path):
    plt.rcParams['font.family'] = 'Times New Roman'
    fig, ax = plt.subplots(figsize=(12, 9), dpi=400)

    female_color_scatter, female_color_line, male_color_scatter, male_color_line, WTP_color = colors

    sns.scatterplot(x='Incr. QALY', y='Incr. Cost', data=female_data, 
                    color=female_color_scatter, alpha=1, label='Female', marker='o', s=10, ax=ax)
    draw_solid_confidence_ellipse(female_data, ax, 'Female', female_color_line)

    sns.scatterplot(x='Incr. QALY', y='Incr. Cost', data=male_data, 
                    color=male_color_scatter, alpha=1, label='Male', marker='o', s=10, ax=ax)
    draw_solid_confidence_ellipse(male_data, ax, 'Male', male_color_line)

    x_values = np.linspace(start=ax.get_xlim()[0]-0.5, stop=ax.get_xlim()[1], num=10)
    y_values = WTP_value * x_values
    plt.plot(x_values, y_values, color=WTP_color, linestyle='--', linewidth=1, label=f'WTP = ${WTP_value}')
    
    ax.set_xlim(-1.0, 2.0)
    ax.set_ylim(-5500, 1500)

    ax.hlines(0, xmin=ax.get_xlim()[0], xmax=ax.get_xlim()[1], colors='k', linestyles='dotted', lw=1)
    ax.vlines(0, ymin=ax.get_ylim()[0], ymax=ax.get_ylim()[1], colors='k', linestyles='dotted', lw=1)

    ax.set_xlabel('Incremental QALYs', fontsize=18)
    ax.set_ylabel('Incremental Costs', fontsize=18)
    ax.tick_params(axis='x', labelsize=16)
    ax.tick_params(axis='y', labelsize=16)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    Female_legend = mlines.Line2D([], [], color=female_color_line, marker='o', linestyle='None',
                                  markersize=6, markeredgewidth=2, label='Female')
    Male_legend = mlines.Line2D([], [], color=male_color_line, marker='o', linestyle='None',
                                markersize=6, markeredgewidth=2, label='Male')
    wtp_legend = mlines.Line2D([], [], color=WTP_color, linestyle='--', linewidth=2, label=f'WTP = ${WTP_value}')
    
    ax.legend(handles=[Female_legend, Male_legend, wtp_legend], fontsize=18)

    plt.savefig(output_pdf_path, format='pdf', bbox_inches='tight')
    plt.show()
