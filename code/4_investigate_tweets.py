import pandas as pd
import numpy as np
import random


pd.options.display.max_colwidth = 300
pd.options.mode.chained_assignment = None

from matplotlib import pyplot as plt
from utils import (import_data,
                    save_data,
                    save_figure)

def get_basic_metrics():

    df = import_data('tweets_condor_EU_false_links_active_2022_04_04.csv')

    print('Number of tweets containing a False condor link', df['id'].count())

    df_url = df.groupby(['clean_url'], as_index = False).size().sort_values(by = 'size', ascending = False)
    df_domain = df.groupby(['full_domain'], as_index = False).size().sort_values(by = 'size', ascending = False)

    return df_url, df_domain

def get_tweets_with_notices():

    df = import_data('tweets_condor_EU_false_links_active_2022_04_04.csv')
    df['total_engagement'] = df['retweet_count'] + df['like_count'] + df['reply_count']

    df_intervention = df.groupby(['intervention_type'], as_index=False).size()
    tweets_intervention = df_intervention['size'].iloc[0]
    df_int = df[df['intervention_type'].notna()]
    save_data(df_int, 'intervention_tweets_condor_EU_false_links_active_2022_04_04.csv', 0)

    df['possibly_sensitive'] = df['possibly_sensitive'].fillna(0)
    df_sensitive = df[df['possibly_sensitive'].isin([1])]
    df_not_sensitive = df[df['possibly_sensitive'].isin([0])]
    possibly_sensitive = len(df_sensitive)
    not_sensitive = len(df_not_sensitive)
    print('poss sensitive', possibly_sensitive)
    print('not sensitive', not_sensitive)
    #save_data(df_sensitive, 'sensitive_tweets_condor_EU_false_links_active_2022_04_04.csv', 0)
    figures = [len(df), tweets_intervention, possibly_sensitive]

    print(figures)

    return figures, df, df_sensitive, df_not_sensitive

def create_donut(figure_name):

    fig, ax = plt.subplots(figsize=(6, 15), subplot_kw=dict(aspect="equal"))

    figures = get_tweets_with_notices()

    ratings = ['Tweets \nwithout notices\n(74078)', 'Tweets with Softintervention (10)', 'Possibly Sensitive Tweets (2944)']
    data = figures

    cmap = plt.get_cmap('coolwarm')
    colors = ['deepskyblue', 'pink', 'lightcoral']

    wedges, texts = ax.pie(data, wedgeprops=dict(width=0.4), startangle=210, colors = colors)

    bbox_props = dict(boxstyle="square,pad=0.2", fc="w", ec="k", lw=0.72)

    kw = dict(arrowprops=dict(arrowstyle="-"),
              bbox=bbox_props, zorder=0, va="center")

    plt.text(0, 0, "Tweets with links\nfact checked as\n false", ha='center', va='center', fontsize=14)

    for i, p in enumerate(wedges):

        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(ratings[i], xy=(x, y), xytext=(1.3*np.sign(x), 1.3*y),
                    horizontalalignment=horizontalalignment, **kw)

    save_figure(figure_name)

def get_list_video_id_community_guidelines():

    df = import_data('messages_videos_youtube_condor_EU_false_links_active_2022_04_04.csv')
    df = df[df['not_found_message'].notna()]
    df = df[df.not_found_message.str.contains('Cette vidéo a été supprimée, car elle ne respectait')]

    list_id = df['video_id'].tolist()

    return list_id

def get_list_available():

    df = import_data('messages_videos_youtube_condor_EU_false_links_active_2022_04_04.csv')
    df = df[df['title'].notna()]
    df = df[~df['information_panel'].notna()]

    list_id = df['video_id'].tolist()

    return list_id

def get_yt_videos_tweets(list_id, message):

    df = import_data('tweets_condor_EU_false_links_active_2022_04_04.csv')

    df_tw_yt = pd.DataFrame(columns=['video_id',
                                    #'engagement_per_tweet',
                                    'number_of_tweets',
                                    'total_engagement',
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
            #engagement_per_tweet = round(total_engagement / number_of_tweets)

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
            #engagement_per_tweet = 0
            max_text = ''
            lng = ''


        df_tw_yt = df_tw_yt.append({'video_id': ID,
                                   'total_engagement': total_engagement,
                                   #'engagement_per_tweet': engagement_per_tweet,
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

def get_yt_tweets_engagement_stats():

    df_suspended = get_yt_videos_tweets(list_id = get_list_video_id_community_guidelines(),
                                        message = 'suspended_community_guidelines')

    print(df_suspended['total_engagement'].mean())
    print(df_suspended['total_engagement'].median())

    df_available_no_panel =  get_yt_videos_tweets(list_id = get_list_available(),
                                        message = 'available_no_info_panel')

    print(df_available_no_panel['total_engagement'].mean())
    print(df_available_no_panel['total_engagement'].median())

def calculate_confidence_interval_median(sample):

    medians = []
    for bootstrap_index in range(1000):
        resampled_sample = random.choices(sample, k=len(sample))
        medians.append(np.median(resampled_sample))

    return np.percentile(medians, 5), np.percentile(medians, 95)

def plot_engagement(df1, df2, df3, df4):

    fig, (ax0, ax1) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [1, 1]})
    fig.set_size_inches(5, 3)

    ax0.bar(
        [0.1], [np.mean(df1['total_engagement'])],
        color='lightcoral', edgecolor='black', width=0.8, alpha=0.7
    )
    ax0.bar(
        [0.9], [np.mean(df2['total_engagement'])],
        color='deepskyblue', edgecolor='black', width=0.8, alpha=0.7
    )
    # low_before, high_before = calculate_confidence_interval_median(df1['total_engagement'].values)
    # ax0.plot([0.1, 0.1], [low_before, high_before], color='black', linewidth=0.9)
    # low_after, high_after = calculate_confidence_interval_median(df2['total_engagement'].values)
    # ax0.plot([0.9, 0.9], [low_after, high_after], color='black', linewidth=0.9)
    ax0.set_xticks([0, 1]),
    ax0.set_xticklabels(['suspended', 'available'])
    ax0.set_xlabel('videos with false link\nshared in tweets')
    ax0.tick_params(axis='x', which='both', length=0)
    ax0.set_xlim(-.5, 1.5)
    ax0.set_ylabel('Average engagement')
    #ax0.set_ylim(-.1, 15)
    #ax0.set_yticks([0, 5, 10, 15, 20])
    ax0.set_frame_on(False)

    ax1.bar(
        [0.1], [np.mean(df3['total_engagement'])],
        color='lightcoral', edgecolor='black', width=0.8, alpha=0.7
    )
    ax1.bar(
        [0.9], [np.mean(df4['total_engagement'])],
        color='deepskyblue', edgecolor='black', width=0.8, alpha=0.7
    )
    # low_before, high_before = calculate_confidence_interval_median(df3['total_engagement'].values)
    # ax1.plot([0.1, 0.1], [low_before, high_before], color='black', linewidth=0.9)
    # low_after, high_after = calculate_confidence_interval_median(df4['total_engagement'].values)
    # ax1.plot([0.9, 0.9], [low_after, high_after], color='black', linewidth=0.9)
    ax1.set_xticks([0, 1]),
    ax1.set_xticklabels(['Possibly', 'not'])
    ax1.set_xlabel('sensitive tweets\nwith false link')
    ax1.tick_params(axis='x', which='both', length=0)
    ax1.set_xlim(-.5, 1.5)
    ax1.set_ylabel('Average engagement')
    #ax1.set_ylim(-.1, 20)
    ax1.set_frame_on(False)

    #fig.suptitle("{} Facebook groups \n self-declared as being under reduced distribution".format(len(df1)))
    fig.tight_layout()
    save_figure('figure_engagement')


if __name__ == '__main__':

    figures, df, df_sensitive, df_not_sensitive = get_tweets_with_notices()
    print(df_not_sensitive['total_engagement'].mean())
    df_suspended = get_yt_videos_tweets(list_id = get_list_video_id_community_guidelines(),
                                        message = 'suspended_community_guidelines')
    df_available = get_yt_videos_tweets(list_id = get_list_available(),
                                        message = 'available_no_info_panel')
    #create_donut(figure_name = 'tweets_notices')
    #get_yt_tweets_engagement_stats()

    plot_engagement(df1 = df_suspended,
                    df2 = df_available,
                    df3 = df_sensitive,
                    df4 = df_not_sensitive)
