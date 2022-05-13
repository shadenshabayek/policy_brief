import os
import numpy as np
import time

from datetime import date
from dotenv import load_dotenv
from time import sleep

from utils import (collect_twitter_data,
                    import_data)

def get_list_links(collection_interupted):

    timestr = time.strftime("%Y_%m_%d")
    df = import_data('condor_EU_false_links_all_2022_05_11.csv')
    df['clean_url_256_character'] = df['clean_url_256_character'].str[:127]
    df['clean_url_256_character'] = [x.split('//')[1] for x in df['clean_url_256_character']]
    df['clean_url_256_character'] = [x.split('http')[0] for x in df['clean_url_256_character']]
    df['clean_url_256_character'] = [x.split('&autoplay=true')[0] for x in df['clean_url_256_character']]
    df['clean_url_256_character'] = [x.split('detail?')[0] for x in df['clean_url_256_character']]
    df['clean_url_256_character'] = [x.split(':')[0] for x in df['clean_url_256_character']]

    list_links = df['clean_url_256_character'].tolist()

    list = ['(' + x + ')' + ' -is:retweet' for x in list_links]
    list.remove('(d.tube/#!/v/pascallegrand17/QmeFTPBQUREHEC8tfssPGhunCNnF7szMySSUdb9vq63qY1) -is:retweet')
    list.append('(d.tube/v/pascallegrand17/QmeFTPBQUREHEC8tfssPGhunCNnF7szMySSUdb9vq63qY1) -is:retweet')

    print('initial list', len(list))

    if collection_interupted == 1:
        df_col = import_data('twitter_links_condor_all_EU_' + timestr  + '.csv')
        list_col = df_col['query'].unique()
        print('collected links', len(list_col))

    list = [x for x in list if x not in list_col]

    print('new list', len(list))
    return list

def main():

    load_dotenv()
    timestr = time.strftime("%Y_%m_%d")
    list_links = get_list_links(collection_interupted = 1)
    print('number of links', len(list_links))

    for query in list_links:
        collect_twitter_data(
            query = query,
            start_time = '2008-06-11T23:00:00Z',
            end_time = '2022-05-11T23:00:05Z',
            bearer_token= os.getenv('TWITTER_TOKEN'),
            filename = os.path.join('.', 'data', 'twitter_links_condor_all_EU_' + timestr  + '.csv'),
            )
        sleep(3)

if __name__=="__main__":

    main()
