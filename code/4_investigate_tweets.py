import pandas as pd
import numpy as np

from matplotlib import pyplot as plt
from utils import (import_data,
                    save_data,
                    save_figure)

def get_basic_metrics():

    df = import_data('tweets_condor_EU_false_links_active_2022_04_04.csv')
    #df = import_data('condor_urls_eu_200_twitter_2022_02_21.csv')
    #print(df.head())
    print('Number of tweets containing a False condor link', df['id'].count())
    print(df.info())
    df_url = df.groupby(['clean_url'], as_index = False).size().sort_values(by = 'size', ascending = False)
    df_domain = df.groupby(['full_domain'], as_index = False).size().sort_values(by = 'size', ascending = False)
    print(df_url.head(30))
    print(df_domain.head(30))
    #print(len(df[df['user_screen_name']].unique()))

def get_tweets_with_notices():

    df = import_data('tweets_condor_EU_false_links_active_2022_04_04.csv')
    #df = import_data('condor_urls_eu_200_twitter_2022_02_21.csv')

    df_intervention = df.groupby(['intervention_type'], as_index=False).size()
    tweets_intervention = df_intervention['size'].iloc[0]
    #print('intervention', tweets_intervention)

    df['possibly_sensitive'] = df['possibly_sensitive'].fillna(0)
    df_sensitive = df[df['possibly_sensitive'].isin([1])]
    possibly_sensitive = len(df_sensitive)
    #print('tweets marked as possibly sensitive', possibly_sensitive)


    #save_data(df_sensitive, 'sensitive_tweets_condor_EU_false_links_active_2022_04_04.csv', 0)

    figures = [len(df), tweets_intervention, possibly_sensitive]
    print(figures)
    return figures

def create_donut(figure_name):

    fig, ax = plt.subplots(figsize=(6, 15), subplot_kw=dict(aspect="equal"))

    figures = get_tweets_with_notices()

    #ratings = df[x].to_list()
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

    #ax.set_title("Tweets containing a link fact checked as false \n in the Condor Dataset", pad = 5)

    save_figure(figure_name)



if __name__ == '__main__':

    #get_basic_metrics()
    get_tweets_with_notices()
    create_donut(figure_name = 'tweets_notices')
