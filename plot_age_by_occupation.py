# -*- coding: utf-8 -*-
"""

Analysis and plotting of the age and occupation of the first recipients of 
COVID-19 vaccines by country
http://wjgsp.com/first-covid-19-vaccines-recipients-by-country

Wagner Gonçalves Pinto
January 2021
wjgsp.com

"""

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import seaborn as sns

if __name__ == '__main__':
    print('Start')
    plt.close('all')
    
    ref_font_size = 7
    colormap = matplotlib.cm.get_cmap('viridis')
    sex_colors = (colormap(100),colormap(0)) # female, male
    marker_size = 4
    
    plt.rc('font', family='serif', size=ref_font_size)
    
    fig_size=(10/2.54,8/2.54)
    legend_prop_dict = dict(
        fancybox=False, 
        fontsize=ref_font_size-2,
        labelspacing=0.4,
        handletextpad=0.25,
        handlelength=1.5,
        columnspacing=0.5,
        )
    
    dataframe_raw = pd.read_csv(
        'data/database_first_covid_vaccination.csv',sep=',',encoding='utf-8')
    
    # ignoring all elements that have no age
    dataframe = dataframe_raw.dropna(axis='index',subset=['age']).copy()
    
    sex_map = dict(male='s', female='o')
    vaccine_map = {'Oxford Univ./AstraZeneca':['o','k'],
                   'Pfizer/BioNTech':['s','r'],
                   'Sinopharm':['v','g'],
                   'Sinovac':['^','b'],
                   'Sputnik V':['D','k'],
                   }
    occupation_map = {'retired':0,
                      'health minister':1,
                      'prime minister':2,
                      'president':3,
                      'nurse':4,
                      'sanitation worker':5, 
                      'medical doctor':6, 
                      }
    
    compare_series_str = lambda series, string: [
        val.strip() == string.strip() for val in series]
    
    fig, ax = plt.subplots(
        nrows=1, ncols=1,
        constrained_layout=True,
        dpi=300,
        figsize=fig_size,
        )
    
    # as indicated on documentation, defining axis before producing
    # the swarmplot
    ax.set_xlim([-0.5,6.5])
    ax.set_ylim([20,104])
    
    # adding grid, only for y axis
    ax.yaxis.grid(True, which='both', alpha=0.5)
    ax.yaxis.set_minor_locator(AutoMinorLocator(5))
    
    ax.xaxis.grid(True, which='minor', alpha=0.5)
    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
    
    ax.grid(linewidth=0.5, which='both', axis='both')
    ax.grid(linewidth=1.0, which='major', axis='both')
    ax.set_axisbelow(True)
    
    sns.swarmplot(
        x=dataframe['occupation'].map(occupation_map),
        y=dataframe['age'],
        hue=list(dataframe['sex']),
        dodge=False,
        size=marker_size,
        palette=sex_colors,
        ax=ax,
        edgecolor='k',
        linewidth=0.5,
        )
    
    # getting the different elements and associating them to the rows in the
    # database
    dataframe.insert(2, 'plotX', dataframe.age.values*0)
    dataframe.insert(2, 'label_loc', 'N')
    
    for index_occupation, occupation in enumerate(occupation_map.keys()):
        scatter_locations = np.array(
            ax.get_children()[index_occupation].get_offsets()
            )
        dataframe_by_occupation = \
            dataframe[dataframe.occupation == occupation].copy()
        count_duplicates = np.zeros(dataframe_by_occupation.shape[0],dtype=int)
        index_case = 0
        for index_row, vaccinated in dataframe_by_occupation.sort_values(
                by='age', ascending=True).iterrows():
            mask_age = np.abs(
                scatter_locations[:,1] - float(vaccinated['age'])) < 0.1
            if np.sum(mask_age) > 1:
                dataframe.loc[index_row,'plotX'] = scatter_locations[
                    mask_age,0][count_duplicates[index_case-1]]
                count_duplicates[index_case] += 1
            else:
                dataframe.loc[index_row,'plotX'] = scatter_locations[mask_age,0]
            index_case += 1
    
    # selecing Sweden point position's directly
    dataframe.loc[dataframe.country == 'Sweden','plotX'] = \
        float(-dataframe.loc[dataframe.country == 'Costa Rica','plotX'])
    
    # adding bands to define major categories
    for band_limits, band_color, band_name in zip(
            ((-0.5, 0.5), (0.5, 3.5), (3.5, 6.5)),
            ('blue','red','green'),
            ('people at\nhigher risk','government\nofficials','front-line\nworkers'),
        ):
        
        color_rgb = list(matplotlib.colors.to_rgba(band_color))
        # modifying transparence
        color_rgb[-1] = 0.15
        # upper band and lower band
        for ymin, ymax in zip((-0.08,1.0),(0.0,1.08)):
            ax.axvspan(
                *band_limits,
                ymin=ymin,ymax=ymax,
                clip_on=False,in_layout=False,
                facecolor=color_rgb,
                edgecolor=[0,0,0,1],
                linewidth=0.5,
                )
        
        annotation_citation = ax.annotate(
            band_name,
            xy=[(band_limits[0]+band_limits[1])/2, 104.5],
            multialignment='center',
            annotation_clip=False,
            xycoords='data',
            ha='center',
            va='bottom',
            fontsize=ref_font_size-1.5,
            rotation=0,
            )
    
    # dictionary indicating the relative position of the label
    # label is placed manually
    label_loc_dict = dict(
        N=dict(ha='center',va='bottom'),
        S=dict(ha='center',va='top'),
        W=dict(ha='right',va='center'),
        E=dict(ha='left',va='center'),
        )
    dataframe.loc[:,'label_loc'] = 'N'
    
    dataframe.insert(2, 'label_offsetX', np.zeros((dataframe.shape[0])))
    dataframe.insert(2, 'label_offsetY', np.zeros((dataframe.shape[0])))
    
    # global definition of labels location
    dataframe.loc[dataframe.label_loc == 'N', 'label_offsetX'] = +.0
    dataframe.loc[dataframe.label_loc == 'N', 'label_offsetY'] = 4
    
    dataframe.loc[dataframe.plotX % 1.0 < 0.999, 'label_loc'] = 'W'
    dataframe.loc[dataframe.label_loc == 'W', 'label_offsetX'] = -.1
    dataframe.loc[dataframe.label_loc == 'W', 'label_offsetY'] = 4
    
    dataframe.loc[dataframe.plotX % 1.0 < 0.5, 'label_loc'] = 'E'
    dataframe.loc[dataframe.label_loc == 'E', 'label_offsetX'] = +.1
    dataframe.loc[dataframe.label_loc == 'E', 'label_offsetY'] = 4
    
    def define_loc_by_country(country,loc,offset=(0,5)):
        mask_country = dataframe.country == country
        dataframe.loc[mask_country,'label_loc'] = loc
        dataframe.loc[mask_country,'label_offsetX'] = offset[0]
        dataframe.loc[mask_country,'label_offsetY'] = offset[1]
    
    # setting labels location country by country
    define_loc_by_country('Austria','E',(+.2,-1.2))
    define_loc_by_country('Belgium','W',(-.0,+3))
    define_loc_by_country('Brazil','E',(+.1,+3))
    define_loc_by_country('Bulgaria','S',(-.1,-4))
    define_loc_by_country('Canada','E',(+.2,-4))
    define_loc_by_country('Chile','E',(+.1,+3))
    define_loc_by_country('Costa Rica','E',(+.2,+0))
    define_loc_by_country('Croatia','E',(+.3,-0.25))
    define_loc_by_country('Czechia','E',(+.15,+4))
    define_loc_by_country('Denmark','S',(+.15,-7.5))
    define_loc_by_country('England','W',(+.05,-17))
    define_loc_by_country('France','S',(+.2,-3))
    define_loc_by_country('Germany','E',(+.2,+1))
    define_loc_by_country('Ireland','E',(+.1,-2))
    define_loc_by_country('India','S',(+.2,-3))
    define_loc_by_country('Italy','E',(+.2,+1))
    define_loc_by_country('Kuwait','W',(0,+4))
    define_loc_by_country('Luxembourg','W',(-.05,-5))
    define_loc_by_country('Malta','E',(+.3,0))
    define_loc_by_country('Mexico','E',(+.2,+3))
    define_loc_by_country('Netherlands','E',(+.1,+2.5))
    define_loc_by_country('Norway','S',(+.1,-4))
    define_loc_by_country('Romania','E',(+.15,-1))
    define_loc_by_country('Serbia','S',(-.1,-4))
    define_loc_by_country('Singapore','W',(-.2,0))
    define_loc_by_country('Spain','E',(+.2,2))
    define_loc_by_country('Slovakia','W',(-.1,-4))
    define_loc_by_country('Sweden','S',(-.04,-3))
    define_loc_by_country('Switzerland','E',(+.3,-2.75))
    define_loc_by_country('Turkey','S',(+.1,-4))
    define_loc_by_country('United States','W',(-.15,+1.5))
    
    # adding text label for all countries
    for index_row, vaccinated in dataframe.iterrows():
        code = vaccinated.code
        occupation_index = vaccinated.map(occupation_map).occupation
        age = vaccinated.age
        
        label = vaccinated.country
        label_font_size = ref_font_size-4.0
        weight = 'regular'
        
        # special labels for lowest and highest ages
        if age == 24:
            label = 'Estonian\n24-years-old\nmedical\nresident'
            label_font_size += 1
            weight='bold'
        if age == 101:
            label = '101-years-old\nGerman senior care\nfacility resident'
            label_font_size += 1
            vaccinated.label_offsetX += 0.5
            vaccinated.label_offsetY += -3.0
            weight='bold'
            
        ax.annotate(
            label,
            fontsize=label_font_size,
            xy=(vaccinated.plotX, age),
            xytext=(
                vaccinated.plotX + vaccinated.label_offsetX,
                age + vaccinated.label_offsetY,
                ),
            textcoords='data',
            rotation=0,
            arrowprops=dict(
                 arrowstyle='-',
                 facecolor='black',
                 linewidth=0.5,
                 shrinkA=0.0, shrinkB=marker_size/2,
                 ),
            bbox=dict(
                 fc='none', ec='none', pad=0.5
                 ),
            **label_loc_dict[vaccinated.label_loc],
            weight=weight,
        )
    
    ax.set_xlabel('', fontsize=ref_font_size)
    ax.set_ylabel('age in years', fontsize=ref_font_size, labelpad=0)
    ax.set_title(
        'Age and occupation of first recipients of\nCOVID-19 vaccine by country',
        pad=20,
        )
    
    ax.set_xticks(list(occupation_map.values()))
    ax.set_xticklabels(
        [label.replace(' ','\n') for label in
             list(occupation_map.keys())],
        fontsize=ref_font_size-1.5,
        
        )
    ax.tick_params(
        axis='x',length=0,pad=7,
        )
    for tick in ax.xaxis.get_major_ticks():
        tick.label1.set_verticalalignment('center')
    
    # remove original legend and building a new one with my parameters
    ax.get_legend().remove()
    handles = [ax.get_children()[0], ax.get_children()[6]]
    ax.legend(
        labels=['male','female'],
        handles=handles,
        **legend_prop_dict,
        )
    
    filename = 'graph_receivers_by_occupation_country'
    print(f'Saving: {filename}.png')
    fig.savefig(filename,dpi=450)
    print('Done')
    