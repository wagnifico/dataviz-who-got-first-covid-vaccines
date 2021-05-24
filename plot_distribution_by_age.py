# -*- coding: utf-8 -*-
"""

Analysis and plotting of the age distribution of the first recipients of 
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

# custom classes to allow using a string as legend handler
# from: https://matplotlib.org/3.3.3/tutorials/intermediate/legend_guide.html
# and
# https://stackoverflow.com/questions/27174425/
#    how-to-add-a-string-as-the-artist-in-matplotlib-legend
#
class AnyObject(object):
    def __init__(self, text, color):
        self.my_text = text
        self.my_color = color

class TextHandler(object):
    def legend_artist(self, legend, orig_handle, fontsize, handlebox):
        x0, y0 = handlebox.xdescent, handlebox.ydescent
        width = handlebox.width
        patch = matplotlib.text.Text(
            x=x0+width/2, y=y0,
            text=orig_handle.my_text,
            color=orig_handle.my_color,
            fontsize=5,
            verticalalignment='baseline', 
            horizontalalignment='center',
            rotation=0, linespacing=None, 
            rotation_mode=None
            )
        handlebox.add_artist(patch)
        return patch

from matplotlib.legend import Legend
Legend.update_default_handler_map({AnyObject: TextHandler()})

if __name__ == '__main__':
    print('Start')
    plt.close("all")
    
    # general plot properties
    ref_font_size = 7
    figure_size=(10/2.54,6/2.54)
    count_text_color = 'gray'
    
    plt.rc('font', family='serif', size=ref_font_size)
    
    legend_prop_dict = dict(
        fancybox=False, 
        fontsize=ref_font_size-1,
        labelspacing=0.4,
        handletextpad=0.25,
        handlelength=1.5,
        columnspacing=0.5,
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
    # ignoring all rows that have no age
    df_vaccine = df_vaccine_raw.dropna(axis='index',subset=['age']).copy()
    
    #### world population database ###
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
    
    df_population['total'] = df_population.sum(axis=1)
    
    mask_both_sexes = df_population['Sex'] == 'Both sexes combined'
    
    age_bins = []
    for col in age_categories:
        age_bins.append(
            int(col.split('-')[0].replace('+',''))
            )
    age_bin_width = (age_bins[1] + age_bins[0])
    age_bins_centers = np.array(age_bins + [105])+age_bin_width/2
    
    # calculating the age distribution
    df_population.loc[5] = \
       ['Age proportion'] + (
           df_population[age_categories + ['total']][mask_both_sexes].values/
               df_population[mask_both_sexes]['total'].values
                   ).tolist()[0]
    
    vaccine_age_heights, bins = np.histogram(
        df_vaccine['age'],
        bins=age_bins + [
            age_bins[-1]+age_bin_width,age_bins[-1]+2*age_bin_width
            ]
        )
    vaccine_age_percentage = [
        (h/sum(vaccine_age_heights))*100 for h in vaccine_age_heights]
    
    ### plots ###
    plot_vaccine_dist = ax.bar(
        age_bins_centers,
        vaccine_age_percentage,
        width=4,
        align='center',
        color='skyblue',
        )
    # adding text annotation with the number of receivers
    text_vertical_offset = .25
    for count, perc, loc in zip(
            vaccine_age_heights,vaccine_age_percentage,age_bins_centers):
        if count > 0:
            ax.annotate(
                str(count),
                xy=[loc,perc+text_vertical_offset],
                ha='center',
                color=count_text_color,
                fontsize=ref_font_size-1,
                )
    legend_text_handle = AnyObject('2', count_text_color)
    
    plot_world_dist = ax.plot(
        np.array(age_bins)+age_bin_width/2,
        df_population.loc[5][1:-1].values*100,
        '-o',
        color='red',
        markeredgecolor='w',
        markeredgewidth=0.25,
        markersize=2.25,
        linewidth=0.75,
        )
    
    # adding grid, only for y axis
    ax.set_ylim([0,15])
    ax.yaxis.grid(True, which='minor')
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax.grid(linewidth=0.5, which='both', axis='y')
    ax.set_axisbelow(True)
    
    ax.set_xlim([0,age_bins[-1]+3*age_bin_width/2])
    x_ticks = np.arange(
        age_bin_width/2, age_bins[-1] + age_bin_width, age_bin_width
        ) 
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(
        (f' {bin_start}-{bin_start+4}' for 
             bin_start in age_bins),
        fontsize=ref_font_size-1,
        rotation=45,
        va='top', # using top and right to set rotation
        ha='right',
    )
    ax.xaxis.set_tick_params(pad=2.5)
        
    ax.set_ylabel('percentage of population, %')
    ax.set_title('Age distribution of first recipients of COVID-19 vaccines')
    
    legend = ax.legend(
        handles=[plot_world_dist[0],
                 legend_text_handle,
                 plot_vaccine_dist[0],
                 ],
        labels=[r'world age structure$^*$',
                r'number of vaccinated',
                r'proportion of recipients',
                ],
        **legend_prop_dict,
        )
    
    # adding text with the citation of UN source
    citation_string = \
        '*: United Nations, Department of Economic and Social Affairs,\n' + \
        'Population Division (2019). World Population Prospects 2019,\n' + \
        'custom data acquired via website. Population in 2015.'
    annotation_citation = ax.annotate(
                citation_string,
                xy=[1.04, 0.5],
                multialignment='center',
                annotation_clip=False,
                xycoords='axes fraction',
                ha='center',
                va='center',
                color=count_text_color,
                fontsize=ref_font_size/2.0,
                rotation=90,
                )
    
    filename = 'graph_distribution_by_age'
    print(f'Saving: {filename}.png')
    fig.savefig(filename,dpi=450)
    print('Done')