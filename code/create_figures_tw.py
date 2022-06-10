import pandas as pd
import numpy as np
import random

pd.options.display.max_colwidth = 300
pd.options.mode.chained_assignment = None

from matplotlib import pyplot as plt
from utils import (import_data,
                   save_data,
                   save_figure)

def get_basic_metrics(filename):

    df = import_data(filename)

    print('Number of tweets containing a False condor link', df['id'].count())

    df_url = df.groupby(['clean_url'], as_index = False).size().sort_values(by = 'size', ascending = False)
    df_domain = df.groupby(['full_domain'], as_index = False).size().sort_values(by = 'size', ascending = False)

    df_initial_links = import_data('condor_EU_false_links.csv')
    list_links_initial = df_initial_links['clean_url'].tolist()
    list_links_tweets = df['clean_url'].unique()

    list = [x for x in list_links_initial if x not in list_links_tweets]
    print(df['clean_url'].nunique())

    return df_url, df_domain

def get_tweets_with_notices(filename):

    df = import_data(filename)

    #the following link is fact-checked as False but its a domain!
    df = df[~df['clean_url'].isin(['https://cienciaysaludnatural.com/'])]

    df['total_engagement'] = df['retweet_count'] + df['like_count'] + df['reply_count']
    df['positive_engagement'] = df['retweet_count'] + df['like_count']

    df_intervention = df.groupby(['intervention_type'], as_index=False).size()
    print(df_intervention)
    tweets_intervention = df_intervention['size'].iloc[0]
    df_int = df[df['intervention_type'].notna()]
    #save_data(df_int, 'intervention_tweets_condor_EU_false_links_active_2022_04_04.csv', 0)

    df['possibly_sensitive'] = df['possibly_sensitive'].fillna(0)
    df_sensitive = df[df['possibly_sensitive'].isin([1])]
    df_not_sensitive = df[df['possibly_sensitive'].isin([0])]
    possibly_sensitive = len(df_sensitive)
    not_sensitive = len(df_not_sensitive)
    tweet_not_sensitive_no_notice = len(df) - tweets_intervention - possibly_sensitive
    print('poss sensitive', possibly_sensitive)
    print('not sensitive', not_sensitive)
    #save_data(df_sensitive, 'sensitive_tweets_condor_EU_false_links_active_2022_04_04.csv', 0)
    figures = []
    figures.append(tweet_not_sensitive_no_notice)
    figures.append(tweets_intervention)
    figures.append(possibly_sensitive)

    print(figures)

    return figures, df, df_sensitive, df_not_sensitive

def create_donut(figure_name, filename):

    fig, ax = plt.subplots(figsize=(6, 15), subplot_kw=dict(aspect='equal'))

    figures, df, df_sensitive, df_not_sensitive = get_tweets_with_notices(filename)

    ratings = ['Tweets \nwithout notices\n or interstitials \n({})'.format(figures[0]),
               'Tweets with a Notice ({})'.format(figures[1]),
               'Tweets with Possibly\n Sensitive interstitial ({})'.format(figures[2])]

    data = figures
    print(data)

    cmap = plt.get_cmap('coolwarm')
    colors = ['deepskyblue', 'pink', 'lightcoral']

    wedges, texts = ax.pie(data, wedgeprops=dict(width=0.4), startangle=210, colors = colors)

    bbox_props = dict(boxstyle='square,pad=0.2', fc='w', ec='k', lw=0.72)

    kw = dict(arrowprops=dict(arrowstyle='-'),
              bbox=bbox_props, zorder=0, va='center')

    plt.text(0, 0, 'Tweets with links\nfact checked as\n false', ha='center', va='center', fontsize=14)

    for i, p in enumerate(wedges):

        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: 'right', 1: 'left'}[int(np.sign(x))]
        connectionstyle = 'angle,angleA=0,angleB={}'.format(ang)
        kw['arrowprops'].update({'connectionstyle': connectionstyle})
        ax.annotate(ratings[i], xy=(x, y), xytext=(1.3*np.sign(x), 1.3*y),
                    horizontalalignment=horizontalalignment, **kw)

    save_figure(figure_name)

def get_list_video_id_community_guidelines(YT_filename):

    df = import_data(YT_filename)
    df = df[df['suspended_message'].notna()]
    df = df[df.suspended_message.str.contains('Cette vidéo a été supprimée, car elle ne respectait')]
    list_id = df['video_id'].tolist()

    return list_id

def get_list_available(YT_filename):

    df = import_data(YT_filename)
    df = df[df['title'].notna()]
    df = df[~df['information_panel'].notna()]
    list_id = df['video_id'].tolist()

    return list_id

def get_yt_videos_tweets(list_id, message, filename):

    df = import_data(filename)
    df_tw_yt = pd.DataFrame(columns=['video_id',
                                    'number_of_tweets',
                                    'total_engagement',
                                    'positive_engagement',
                                    'total_retweet_count',
                                    'total_like_count',
                                    'total_reply_count',
                                    'max_text',
                                    'lang',
                                    'tweet_ID_max_text',
                                    'message'])

    for ID in list_id:
        df_tw = df[df.text.str.contains(ID)]

        if len(df_tw) > 0 :
            number_of_tweets = df_tw['id'].count()
            total_retweet_count = df_tw['retweet_count'].sum()
            total_like_count = df_tw['like_count'].sum()
            total_reply_count = df_tw['reply_count'].sum()
            total_engagement = total_retweet_count + total_like_count + total_reply_count
            positive_engagement = total_retweet_count + total_like_count

            df_tw['length'] = df_tw['text'].apply(len)
            max_l = max(df_tw['length'])
            max_text = df_tw[df_tw['length'] == max_l]['text'].iloc[0]
            lang = df_tw[df_tw['length'] == max_l]['lang'].iloc[0]
            tweet_ID_max_text = df_tw[df_tw['length'] == max_l]['id'].iloc[0]

        else :
            number_of_tweets = 0
            total_retweet_count = 0
            total_like_count = 0
            total_reply_count = 0
            total_engagement = 0
            positive_engagement = 0
            max_text = ''
            lng = ''

        df_tw_yt = df_tw_yt.append({'video_id': ID,
                                   'total_engagement': total_engagement,
                                   'positive_engagement': positive_engagement,
                                   'number_of_tweets': number_of_tweets,
                                   'total_retweet_count': total_retweet_count,
                                   'total_like_count': total_like_count,
                                   'total_reply_count': total_reply_count,
                                   'max_text': max_text,
                                   'lang' : lang,
                                   'tweet_ID_max_text': tweet_ID_max_text,
                                   'message': message
                                   }, ignore_index=True)

    df_tw_yt = df_tw_yt.sort_values(by = 'total_engagement', ascending = False)
    df_tw_yt = df_tw_yt.drop_duplicates(subset = ['video_id'])
    print(df_tw_yt)
    save_data(df_tw_yt, 'tweets_with_yt_videos.csv', 1)
    return df_tw_yt

def get_yt_tweets_engagement_stats(filename):

    df_suspended = get_yt_videos_tweets(list_id = get_list_video_id_community_guidelines(),
                                        message = 'suspended_community_guidelines',
                                        filename = filename)

    print(df_suspended['total_engagement'].mean())
    print(df_suspended['total_engagement'].median())

    df_available_no_panel =  get_yt_videos_tweets(list_id = get_list_available(),
                                        message = 'available_no_info_panel',
                                        filename = filename)

    print(df_available_no_panel['total_engagement'].mean())
    print(df_available_no_panel['total_engagement'].median())

def plot_engagement(df1, df2, df3, df4, stat, title, type_enagement):

    fig, (ax0, ax1) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [1, 1]})
    fig.set_size_inches(5, 3)

    if stat == 'Average':
        ax0.bar(
            [0.1], [np.mean(df1[type_enagement])],
            color='lightcoral', edgecolor='black', width=0.8, alpha=0.7
        )
        ax0.bar(
            [0.9], [np.mean(df2[type_enagement])],
            color='deepskyblue', edgecolor='black', width=0.8, alpha=0.7
        )
    elif stat == 'Median':
        ax0.bar(
            [0.1], [np.median(df1[type_enagement])],
            color='lightcoral', edgecolor='black', width=0.8, alpha=0.7
        )
        ax0.bar(
            [0.9], [np.median(df2[type_enagement])],
            color='deepskyblue', edgecolor='black', width=0.8, alpha=0.7
        )

    ax0.set_xticks([0, 1]),
    ax0.set_xticklabels(['suspended', 'available'])
    ax0.set_xlabel('videos with false link\nshared in tweets')
    ax0.tick_params(axis='x', which='both', length=0)
    ax0.set_xlim(-.5, 1.5)
    ax0.set_ylabel('{} engagement'.format(title))
    ax0.set_frame_on(False)

    if stat == 'Average':
        ax1.bar(
            [0.1], [np.mean(df3[type_enagement])],
            color='lightcoral', edgecolor='black', width=0.8, alpha=0.7
        )
        ax1.bar(
            [0.9], [np.mean(df4[type_enagement])],
            color='deepskyblue', edgecolor='black', width=0.8, alpha=0.7
        )
    elif stat == 'Median':
        ax1.bar(
            [0.1], [np.median(df3[type_enagement])],
            color='lightcoral', edgecolor='black', width=0.8, alpha=0.7
        )
        ax1.bar(
            [0.9], [np.median(df4[type_enagement])],
            color='deepskyblue', edgecolor='black', width=0.8, alpha=0.7
        )

    ax1.set_xticks([0, 1]),
    ax1.set_xticklabels(['Possibly', 'not'])
    ax1.set_xlabel('sensitive tweets\nwith false link')
    ax1.tick_params(axis='x', which='both', length=0)
    ax1.set_xlim(-.5, 1.5)
    ax1.set_ylabel('{} engagement'.format(title))
    ax1.set_frame_on(False)

    fig.tight_layout()
    save_figure('figure_engagement_{}'.format(title))

def create_figures(TW_filename, YT_filename):

    figures, df, df_sensitive, df_not_sensitive = get_tweets_with_notices(filename = TW_filename)

    df_suspended = get_yt_videos_tweets(list_id = get_list_video_id_community_guidelines(YT_filename = YT_filename),
                                        message = 'suspended_community_guidelines',
                                        filename = TW_filename)

    df_available = get_yt_videos_tweets(list_id = get_list_available(YT_filename = YT_filename),
                                        message = 'available_no_info_panel',
                                        filename = TW_filename)

    create_donut(figure_name = 'tweets_notices_2022_05_13_minet',
                filename = TW_filename)

    plot_engagement(df1 = df_suspended,
                    df2 = df_available,
                    df3 = df_sensitive,
                    df4 = df_not_sensitive,
                    stat = 'Average',
                    title = 'Average total ',
                    type_enagement = 'total_engagement')

    plot_engagement(df1 = df_suspended,
                    df2 = df_available,
                    df3 = df_sensitive,
                    df4 = df_not_sensitive,
                    stat = 'Average',
                    title = 'Average positive ',
                    type_enagement = 'positive_engagement')

    get_basic_metrics(filename = TW_filename)

def main():

    #csv which contains tweets collect with minet, using links fact-checked as false as a list of queries
    TW_filename = 'tweets_condor_EU_false_links_active_2022_05_12.csv'
    #csv which contains the messages returned by scraping the links corresponding to YouTube videos fact-checked as False
    YT_filename = 'messages_videos_youtube_condor_EU_false_links_active_2022_04_04.csv'

    create_figures(TW_filename = TW_filename,
                   YT_filename = YT_filename)

if __name__ == '__main__':

    main()
