import os
from datetime import datetime, timedelta, date

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches #new addition to create the boxes in the legend for the shaded areas
import ural

from utils import (import_data, save_figure)


def clean_buzzsumo_data(df):

    df['date'] = [datetime.fromtimestamp(x).date() for x in df['published_date']]
    df['date'] = pd.to_datetime(df['date'])

    df = df.drop_duplicates(subset=['url'])
    df = df.sort_values(by = 'date')

    return df

def arrange_plot(ax, df, website):

    plt.legend()

    ax.set_frame_on(False)
    ax.grid(axis="y")
    plt.locator_params(axis='y', nbins=4)

    plt.xticks(rotation = 45)
    ax.xaxis.set_tick_params(length=0)

    if website == 'ei':
        plt.axvspan(np.datetime64('2020-04-14'), np.datetime64('2020-07-07'),
                ymin=0, ymax=200000, facecolor='k', alpha=0.05)

    elif website == 'reseauinternational.net':
        plt.axvspan(np.datetime64('2020-03-24'), np.datetime64('2020-06-01'),
                        ymin=0, ymax=200000, facecolor='k', alpha=0.05)

    plt.xlim(np.min(df['date']), np.max(df['date']))

def create_buzzsumo_figure(df, website, max_y1, max_y2, title):

    print()
    df = clean_buzzsumo_data(df)

    if website == 'ei':
        list_dates = ["2020-04-15",
                    "2020-05-05",
                    "2020-07-05",
                    "2020-10-25",
                    "2020-11-14",
                    "2020-11-17",
                    "2020-12-31"]

    elif website == 'reseauinternational.net':
        list_dates = ["2020-01-13",
                    "2020-03-25",
                    "2020-05-20",
                    "2020-05-31",
                    "2020-08-31",
                    "2020-10-06",
                    "2020-11-23"]

    fig = plt.figure(figsize=(10, 4))
    fig.suptitle('{} (data from Buzzsumo)'.format(title))

    ax = plt.subplot(111)
    plt.plot(df.resample('D', on = 'date')['facebook_comments'].mean(),
        label ="Facebook comments per article",
        color = 'lightskyblue')
    plt.plot(df.resample('D', on = 'date')['facebook_shares'].mean(),
        label ="Facebook shares per article",
        color = 'royalblue')
    plt.plot(df.resample('D', on = 'date')['facebook_likes'].mean(),
        label ="Facebook reactions (likes, ...) per article",
        color='navy')
    arrange_plot(ax, df, website)

    for d in list_dates :
        plt.axvline(np.datetime64(d), color='grey', linestyle='--')

    plt.ylim(-50, max_y1)

    plt.tight_layout()#
    save_figure('facebook_buzzsumo_{}_1.png'.format(website))#

    fig = plt.figure(figsize=(10, 4)) #
    fig.suptitle('{} (data from Buzzsumo)'.format(title))

    ax = plt.subplot(111) #
    plt.plot(df.resample('D', on='date')['date'].agg('count'),
            label='Number of articles published per day',
            color='grey')
    arrange_plot(ax, df, website)

    for d in list_dates :
        plt.axvline(np.datetime64(d),
        color='grey',
        linestyle='--')

    plt.ylim(0, max_y2)

    plt.tight_layout()
    save_figure('facebook_buzzsumo_{}_2.png'.format(website))

def create_figures():

    create_buzzsumo_figure( df =import_data('posts_url_ei_org_2022-04-04.csv') ,
                            website = 'ei' ,
                            max_y1 = 7000,
                            max_y2 = 40,
                            title = 'europe-israel.org',
                            )

    create_buzzsumo_figure( df =import_data('posts_url_2022-04-04.csv') ,
                            website = 'reseauinternational.net' ,
                            max_y1 = 2500,
                            max_y2 = 30,
                            title = 'reseauinternational.net',
                            )
if __name__ == '__main__':

    create_figures()
