import pandas as pd
import numpy as np
import time

from datetime import date
from utils import (import_data,
                    save_data,
                    save_figure)

pd.options.display.max_colwidth = 300
pd.options.mode.chained_assignment = None

def get_false_urls ():

    df = import_data('./tpfc-recent.csv')

    df_agg = df.groupby(['tpfc_rating'],
            as_index = False).size().sort_values(by = 'size', ascending = False)

    df_agg = df_agg.rename(columns = {'size': 'number of links'})

    print('Condor Dataset by rating : \n (First fact check date',
          df['tpfc_first_fact_check'].min(),
          ') \n (Last fact check date',
          df['tpfc_first_fact_check'].max(),
          ') \n',
          df_agg)

    #save_data(df_agg, 'aggregate_links_condor.csv', 0)

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

def main():

    df_condor = get_false_urls ()
    df, df_Europe = get_continents_top_shares(df_condor)
    df_EU = keep_top_99_EU (df_Europe)

if __name__=="__main__":

    main()
