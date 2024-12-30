import matplotlib.pyplot as plt
import numpy as np

def create_summary_plot_bar(df_plot, colors, output_pdf_path):
    stroke_event_vars = ['t_IS_event', 't_HS_event', 't_US_event']
    stroke_death_vars = ['t_IS_death', 't_HS_death', 't_US_death']
    chd_vars = ['t_chd_event', 't_chd_death']

    row_vars = [stroke_event_vars, stroke_death_vars, chd_vars]

    row_titles = ['Stroke Events', 'Stroke Deaths', 'CHD Events/Deaths']
    y_labels = ['Stroke Events', 'Stroke Deaths', 'CHD Events/Deaths']

    genders = ['both', 'female', 'male']
    col_titles = ['Both', 'Female', 'Male']

    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['font.size'] = 18

    stroke_colors = {
        't_IS_event': colors[0],
        't_HS_event': colors[1],
        't_US_event': colors[2],
        't_IS_death': colors[0],
        't_HS_death': colors[1],
        't_US_death': colors[2],
    }
    chd_colors = {
        't_chd_event': colors[3],
        't_chd_death': colors[4],
    }

    variable_mapping = {
        't_IS_event': 'Ischemic stroke',
        't_HS_event': 'Hemorrhagic stroke',
        't_US_event': 'Undetermined stroke',
        't_IS_death': 'Ischemic stroke',
        't_HS_death': 'Hemorrhagic stroke',
        't_US_death': 'Undetermined stroke',
        't_chd_event': 'CHD events',
        't_chd_death': 'CHD deaths'
    }

    fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(18, 18), dpi=200, sharey='row')
    fig.subplots_adjust(wspace=0.5, hspace=0.5)

    subplot_labels = [chr(65+i) for i in range(9)]  # A, B, C, D, E, F, G, H, I

    label_index = 0
    bar_width = 0.15

    for row, variables in enumerate(row_vars):
        for col, gender in enumerate(genders):
            ax = axes[row, col]
            all_years = sorted(df_plot[(df_plot['Gender'] == gender) 
                                & (df_plot['Variable'].isin(variables))]['Year'].unique())

            x_positions = np.arange(len(all_years))
            
            for i, var in enumerate(variables):
                subset = df_plot[(df_plot['Gender'] == gender) & (df_plot['Variable'] == var)]
                subset = subset.set_index('Year').reindex(all_years)
                
                y = subset['Change_mean'].values / 1000
                ci_lower = subset['Change_ci_lower'].values / 1000
                ci_upper = subset['Change_ci_upper'].values / 1000
                
                if var in stroke_colors:
                    color = stroke_colors[var]
                else:
                    color = chd_colors[var]
                
                bar_x = x_positions + i * bar_width
                
                bars = ax.bar(bar_x, y, bar_width, label=variable_mapping[var], alpha=0.8, 
                                color=color, edgecolor='black', linewidth=0.5, zorder=3)
                
                yerr_lower = np.abs(y - ci_lower)
                yerr_upper = np.abs(ci_upper - y)
                
                ax.errorbar(bar_x, y, yerr=[yerr_lower, yerr_upper], fmt='none', ecolor='black', 
                            capsize=5, elinewidth=1, capthick=1, alpha=0.7)

            ax.set_title(f'{col_titles[col]} {row_titles[row]}', fontsize=18)
            
            if col == 0:
                ax.set_ylabel('Change in (Intervention - Base), in thousands', fontsize=18)

            ax.set_xticks(x_positions + (len(variables)-1)*bar_width/2)
            ax.set_xticklabels(all_years)

            if row < 2:
                ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
            
            if col == 2:
                ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=16)

            if row == 0:
                ax.spines['top'].set_visible(True)
                ax.spines['bottom'].set_visible(False)
                ax.spines['right'].set_visible(False)
            elif row == 2:
                ax.spines['bottom'].set_visible(True)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.set_xlabel('Year', fontsize=18)
            else:
                ax.spines['top'].set_visible(True)
                ax.spines['bottom'].set_visible(False)
                ax.spines['right'].set_visible(False)

            ax.spines['left'].set_visible(True)

            x_position = -0.1 if col == 0 else -0.05
            ax.text(x_position, 1.05, subplot_labels[label_index], transform=ax.transAxes, 
                    fontsize=18, fontweight='bold', va='top', ha='right')

            label_index += 1

    plt.tight_layout()
    plt.savefig(output_pdf_path, format='pdf')
    plt.show()
