import pandas as pd

pd.options.display.max_colwidth = 300
pd.options.mode.chained_assignment = None

from utils import (import_data,
                    save_data)


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

    df = import_data('condor_EU_false_links_report_2022_04_04.csv')
    df_active, df_yt = get_active_links(df)

if __name__ == '__main__':

    main()
