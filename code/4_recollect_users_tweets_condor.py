import numpy as np
import os
import time


from datetime import date
from dotenv import load_dotenv
from time import sleep

from utils import (recollect_tweets_by_id,
                    import_data)



def get_id_list(updated_list):

    df = import_data('tweets_condor_EU_false_links_active_2022_04_04.csv')

    if updated_list == 0 :

        list = df['id'].dropna().unique()
        print(len(list))
    elif updated_list == 1 :

        timestr = time.strftime("%Y_%m_%d")
        df_collected = import_data('tweets_recollect_condor_' + timestr  + '.csv')

        list1 = df_collected['id'].to_list()
        print(len(list1))

        list2 = df['id'].dropna().unique()

        list = [x for x in list2 if x not in list1]

    return list


if __name__=="__main__":

    list = get_id_list(updated_list = 0)
    timestr = time.strftime("%Y_%m_%d")

    load_dotenv()
    recollect_tweets_by_id(bearer_token = os.getenv('TWITTER_TOKEN'),
                            List_id = get_id_list(updated_list = 0),
                            file_name = 't_tweets_recollect_condor_' + timestr  + '.csv')
