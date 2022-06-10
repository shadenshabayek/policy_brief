import pandas as pd
import numpy as np
import time

from datetime import date
from utils import (import_data,
                    save_data,
                    save_figure)

pd.options.display.max_colwidth = 300
pd.options.mode.chained_assignment = None

def get_false_urls (group_small_cat):

    df = import_data('./tpfc-recent.csv')

    df_agg = df.groupby(['tpfc_rating'],
            as_index = False).size().sort_values(by = 'size', ascending = False)

    df_agg = df_agg.rename(columns = {'size': 'number of links'})
    print(df_agg)
    print('Condor Dataset by rating : \n (First fact check date',
          df['tpfc_first_fact_check'].min(),
          ') \n (Last fact check date',
          df['tpfc_first_fact_check'].max(),
          ') \n',
          df_agg)

    count_satire = df_agg.loc[df_agg['tpfc_rating'] == 'satire', 'number of links'].iloc[0]
    count_opinion = df_agg.loc[df_agg['tpfc_rating'] == 'opinion', 'number of links'].iloc[0]
    count_prank_generator = df_agg.loc[df_agg['tpfc_rating'] == 'prank generator', 'number of links'].iloc[0]
    count_prank_altered = df_agg.loc[df_agg['tpfc_rating'] == 'fact checked as altered media', 'number of links'].iloc[0]
    count_miss = df_agg.loc[df_agg['tpfc_rating'] == 'fact checked as missing context', 'number of links'].iloc[0]
    drop = ['satire', 'opinion', 'prank generator', 'fact checked as altered media', 'fact checked as missing context']

    if group_small_cat == 1:
        nb_satire_opinion = count_satire + count_opinion
        nb_other = count_prank_generator + count_prank_altered + count_miss
        df_agg = df_agg.append({'tpfc_rating': 'satire or opinion', 'number of links': nb_satire_opinion}, ignore_index=True)
        df_agg = df_agg.append({'tpfc_rating': 'other', 'number of links': nb_other}, ignore_index=True)
        df_agg = df_agg[~df_agg['tpfc_rating'].isin(drop)].sort_values(by = 'number of links', ascending = False)

    save_data(df_agg, 'aggregate_links_condor_2022_06_10.csv', 0)
    print(df_agg)
    df = df[df['tpfc_rating'] == 'fact checked as false']
    return df

def get_dict_continents():

    country_code = import_data('country_codes_wikipedia.csv')
    country_code['continent_code' ] = country_code['continent_code'].fillna('North America')

    continents = ['EU',
                  'AF',
                  'AS',
                  'OC',
                  'SA',
                  'AN',
                  'North America']
    dct = {}
    for i in continents:
        dct['list_%s' % i] = country_code[
        country_code['continent_code'].isin([i])]['country_code'].tolist()

    return dct

def get_continents_top_shares(df):

    dct = get_dict_continents()

    continent_code = dct.keys()
    continent_name = ['Europe',
                      'Africa',
                      'Asia',
                      'Oceania',
                      'South America',
                      'Antartica',
                      'North America']

    zipped_lists = zip(continent_code, continent_name)

    df['continent'] = 'other'

    for (x,y) in zipped_lists :
        df['continent'] = np.where(
                          df['public_shares_top_country'].isin(dct[x]), y, df['continent'])

    save_data(df, 'public_shares_top_country_continent.csv', 0)
    df_Europe = df[df['continent'].isin(['Europe'])]

    print('False Links in condor by continent: \n',
          df.groupby(['continent'], as_index = False).size())

    return df, df_Europe

def keep_top_99_EU (df):

    nb_links = df.groupby(['public_shares_top_country'],
               as_index = False).size().sort_values(by = 'size', ascending = False)

    list_top_EU_countries = nb_links[nb_links['size'] > 99]['public_shares_top_country'].to_list()

    remove = ['UA',
              'RS']

    list_EU_countries = list(set(list_top_EU_countries) - set(remove))
    df = df[df['public_shares_top_country'].isin(list_EU_countries)]
    print('Number of False links all time EU:', len(df))

    df['date'] = pd.to_datetime(df['first_post_time']).dt.date
    df = df.reset_index()
    df = df[(df['date'] > date(2020, 1, 1))]

    print('Number of False links EU, since Jan 2020:', len(df))
    print('The ten EU countries we study are, appearing over 100 times, and removing RS and UA: \n', list_EU_countries)
    print(df[df['public_shares_top_country'].isin(['FR'])].groupby(['parent_domain'], as_index = False).size().sort_values(by = 'size', ascending = False).head(40))

    save_data(df, 'condor_EU_false_links.csv', 0)

    return df

def get_active_links(df):

    print('there are ', len(df), ' False links in the Condor dataset (10 EU countries since 2020)')

    df_active = df[df['status'] == 200]
    print('there are ', len(df_active), ' active False links in the Condor dataset (10 EU countries since 2020)')

    df_yt = df_active[df_active['parent_domain'] == 'youtube.com']
    print('there are ', len(df_yt), ' active youtube links (links opens but might be suspended)' )

    df_yt['yt_video_id'] = df_yt['clean_url'].str.split('=').str[1]
    #save_data(df_yt, 'youtube_condor_EU_false_links_active.csv', 0)

    df_active['clean_url_256_character'] = df_active['clean_url'].str[:256]
    #save_data(df_active, 'condor_EU_false_links_active_2022_04_04.csv', 0)

    df['clean_url_256_character'] = df['clean_url'].str[:256]
    save_data(df, 'condor_EU_false_links_all_2022_05_11.csv', 0)

    return df_active, df_yt

def main():

    df_condor = get_false_urls ()
    df, df_Europe = get_continents_top_shares(df_condor)
    df_EU = keep_top_99_EU (df_Europe)

    df = import_data('condor_EU_false_links_report_2022_04_04.csv')
    df_active, df_yt = get_active_links(df)

if __name__=="__main__":

    #main()
    get_false_urls (group_small_cat = 1)
