# -*- coding: utf-8 -*-
"""

Analysis and plotting of the gender distribution of the first recipients of 
COVID-19 vaccines
http://wjgsp.com/first-covid-19-vaccines-recipients-by-country

Wagner Gonçalves Pinto
January 2021
wjgsp.com

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.text
from matplotlib.ticker import AutoMinorLocator

if __name__ == '__main__':
    print('Start')
    plt.close("all")
    
    # general plot properties
    ref_font_size = 7
    note_font_size = 3
    figure_size=(10/2.54,4/2.54)
    count_text_color = 'gray'
    colormap = matplotlib.cm.get_cmap('viridis')
    sex_colors = (colormap(0),colormap(100)) # male, female
    
    plt.rc('font', family='serif', size=ref_font_size)
    
    legend_prop_dict = dict(
        fancybox=False, 
        fontsize=ref_font_size-1,
        labelspacing=0.4,
        handletextpad=0.25,
        handlelength=1.5,
        columnspacing=1.0,
        )
    
    fig, ax = plt.subplots(
        nrows=1, ncols=1,
        constrained_layout=True,
        dpi=300,
        figsize=figure_size,
        )
    
    #### vaccination database ###
    df_vaccine_raw = pd.read_csv(
        'data/database_first_covid_vaccination.csv',sep=',',encoding='utf-8')
    # ignoring all rows that have no sex info
    df_vaccine = df_vaccine_raw.dropna(axis='index',subset=['sex']).copy()
    
    vaccine_total = len(df_vaccine.index)
    vacine_male_proportion = \
        np.sum(df_vaccine['sex'] == 'male')/vaccine_total
    vacine_female_proportion = 1 - vacine_male_proportion
    
    #### world population database - UN ###
    df_population = pd.read_csv(
        'data/database_world_population_by_UN_CC-BY-3.0-IGO.csv',
        delimiter=',',encoding='utf-8'
        )
    year_to_consider = 2015
    mask_year = df_population['Time'] == year_to_consider
    df_population = df_population[mask_year]
    # remove year info, since only `year_to_consider` is considered
    df_population = df_population.drop(['Time'],axis=1)
    
    age_categories = list(df_population.columns)
    age_categories.remove('Sex')
    
    mask_both_sexes = df_population['Sex'] == 'Both sexes combined'
    
    df_population['total'] = df_population.sum(axis=1)
    df_population.loc[4] = \
            ['Male proportion'] + (
                df_population[age_categories + ['total']][
                    df_population['Sex'] == 'Male'].values/ \
                df_population[age_categories + ['total']][
                    mask_both_sexes].values
                ).tolist()[0]
            
    df_population.loc[5] = \
            ['Female proportion']+ (
                1 - df_population[age_categories + ['total']][
                    df_population['Sex'] == 'Male proportion'].values
                ).tolist()[0]
    world_male_proportion = df_population.loc[4]['total']
    
    # calculating the proportion of females over 65 years old
    age_cat_elder = 6 # 8 for 65, 6 for 75
    df_elderly_pop = df_population.copy()
    df_elderly_pop = df_elderly_pop[['Sex'] + \
        age_categories[-age_cat_elder:] + ['total']]
    
    # recalculating male/female ratios
    mask_both_sexes = df_elderly_pop['Sex'] == 'Both sexes combined'
    df_elderly_pop.total = 0
    df_elderly_pop.total = df_elderly_pop.sum(axis=1)
    df_elderly_pop.loc[4] = \
            ['Male proportion'] + (
                df_elderly_pop[age_categories[-age_cat_elder:] + ['total']][
                    df_population['Sex'] == 'Male'].values/ \
                df_elderly_pop[age_categories[-age_cat_elder:] + ['total']][
                    mask_both_sexes].values
                ).tolist()[0]
            
    df_elderly_pop.loc[5] = \
            ['Female proportion']+ (
                1 - df_elderly_pop[age_categories[-age_cat_elder:] + ['total']][
                    df_elderly_pop['Sex'] == 'Male proportion'].values
                ).tolist()[0]
    elderly_male_proportion = df_elderly_pop.loc[4]['total']
    
    #### nurse population database - WHO ###
    df_health_workers = pd.read_csv(
        'data/database_sex_distribution_health_workers_by_WHO_CC-BY-NC-SA-3.0-IGO.csv',
        delimiter=',',encoding='utf-8'
        )
    # renaming columns
    df_health_workers.columns = (
        'country','year',
        'male_doctor_perc','female_doctor_perc',
        'male_nursing_perc','female_nursing_perc',
        )
    # ignoring all rows that have no nursing staff numbers
    df_health_workers = df_health_workers.dropna(
        axis='index',subset=['male_nursing_perc'])
    
    # selecting the latest available per country
    for country in df_health_workers['country'].unique():
        mask_country = df_health_workers['country'] == country
        df_workers_country = df_health_workers[mask_country]
        
        year_to_remain = df_workers_country['year'].max()
        # dropping all other years
        mask_to_drop = mask_country & \
            (df_health_workers.year != year_to_remain)
        
        df_health_workers = df_health_workers[~mask_to_drop]
        
    # defining the gender ratio for the nursing personel based on the average
    # among all the countries listed
    nursing_male_proportion = df_health_workers.male_nursing_perc.mean()/100
    nursing_female_proportion = 1 - nursing_male_proportion
    
    def plot_stacked_bar(
            ax,y,left_proportion,height=0.9,font_size=ref_font_size):
        # function to plot stacked bars
        right_proportion = 1 - left_proportion
        
        bars = []
        bars.append(
            ax.barh(
                y=y,
                width=left_proportion,
                height=height,
                color=sex_colors[0],
                edgecolor='k',
                linewidth=0.5,
               )
            )
        bars.append(
            ax.barh(
                y=y,
                width=right_proportion,
                height=height,
                left=left_proportion,
                color=sex_colors[1],
                edgecolor='k',
                linewidth=0.5,
               )
            )
        # adding text on bars
        central_bands = \
            [left_proportion/2, left_proportion + right_proportion/2]
        for value, location in zip(
                (left_proportion,right_proportion),central_bands):
            ax.annotate(
                f'{value*100:.1f}%',
                xy=[location,y],
                ha='center',
                va='center',
                color='w',
                fontsize=font_size,
                )
        
        return bars
    
    y_ticks = [0,-0.9,-1.6,-2.3]
    
    plot_stacked_bar(
        ax,y_ticks[0],vacine_male_proportion)
    plot_stacked_bar(
        ax,y_ticks[1],world_male_proportion,
        height=0.6,font_size=ref_font_size-1.5)
    plot_stacked_bar(
        ax,y_ticks[2],elderly_male_proportion,
        height=0.6,font_size=ref_font_size-1.5)
    bars = plot_stacked_bar(
        ax,y_ticks[3],nursing_male_proportion,
        height=0.6,font_size=ref_font_size-1.5)
    
    legend_prop_dict = dict(
        fancybox=False, 
        fontsize=ref_font_size-2,
        labelspacing=0.4,
        handletextpad=0.25,
        handlelength=1.5,
        columnspacing=0.5,
        )
    
    legend = ax.legend(
        handles=bars,
        labels=['male','female'],
        loc='upper center',
        ncol=2,
        bbox_to_anchor=(0.5, 1.225),
        **legend_prop_dict,
        )
    
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(
        ('first vaccine\nrecipients',
         'world$^*$\n(all ages)',
         'world$^*$\n(75+ years old)',
         'nursing\npersonel$^{**}$'),
        fontsize=ref_font_size-1,
        )
    for tick in ax.yaxis.get_major_ticks()[1:]:
        tick.label1.set_fontsize(ref_font_size-2.5)
        
    ax.yaxis.set_tick_params(
        pad=2.5, which=u'both', length=0
        )    
    ax.xaxis.set_tick_params(pad=1.5)
    ax.set_xlim([0,1])
    
    ax.set_xticks([0,0.25,0.5,0.75,1])
    ax.set_xticklabels(
        ['0% male\n100% female',
         '25% - 75%','50% - 50%','75% - 25%',
         '100% male\n0% female'],
        fontsize=ref_font_size-1,
        )
    # adding grid, only for x axis
    ax.xaxis.grid(True, which='minor')
    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax.grid(linewidth=0.5, which='both', axis='x')
    ax.set_axisbelow(True)
    
    ax.set_title(
        'Gender distribution of first recipients of COVID-19 vaccine',
        pad=16,
        )

    # adding text with the citation of UN and WHO sources
    citation_string = \
        '$^*$: United Nations, Department of Economic and Social Affairs, ' + \
        'Population Division (2019). World Population ' + \
        'Prospects 2019, custom data acquired via website. Based \n'+ \
        'on population in 2015; ' + \
        '$^{**}$: Average of per country ratios. World Health Organization. ' + \
        'Global Health Observatory data repository, ' + \
        'Sex distribution of health workers '
    
    annotation_citation = ax.annotate(
                citation_string,
                xy=[-0.2, -0.3],
                multialignment='left',
                annotation_clip=False,
                xycoords='axes fraction',
                ha='left',
                va='top',
                color=count_text_color,
                fontsize=note_font_size,
                rotation=0,
                linespacing=0.25*note_font_size,
                )
    
    filename = 'graph_distribution_by_sex'
    print(f'Saving: {filename}.png')
    fig.savefig(filename,dpi=450)
    print('Done')
    