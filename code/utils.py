#from __future__ import absolute_import

import ast
import csv
import datetime
import glob
import json
import time
import os
import os.path
import pandas as pd
import pickle
import numpy as np
import requests

from dotenv import load_dotenv


from csv import writer
from functools import reduce
from time import sleep
from matplotlib import pyplot as plt
from minet import multithreaded_resolve
from pandas.api.types import CategoricalDtype
from ural import get_domain_name
from ural import is_shortened_url

def import_data(file_name):

    data_path = os.path.join('.', 'data', file_name)
    df = pd.read_csv(data_path, low_memory=False)
    return df

def save_figure(figure_name):

    figure_path = os.path.join('.', 'figures', figure_name)
    plt.savefig(figure_path, bbox_inches='tight')
    print('The {} figure is saved.'.format(figure_name))

def save_data(df, file_name, append):

    file_path = os.path.join('.', 'data', file_name)

    if append == 1:
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(file_path, index=False)

    print(' {} is saved.'.format(file_name))


def create_url_recollect(ids):
    tweet_fields = "tweet.fields=author_id,public_metrics,referenced_tweets,withheld,conversation_id"
    expansions = "referenced_tweets.id.author_id"
    media_fields = "public_metrics"
    user = "user.fields=username,name,id"
    url = "https://api.twitter.com/2/tweets?{}&{}&expansions={}&{}".format(ids, tweet_fields,  expansions,user)
    return url

def create_headers_recollect(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def connect_to_endpoint_recollect(url, headers):
    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

def write_results_recollect_tweets(json_response, filename):

    with open(filename, "a") as tweet_file:

        writer = csv.DictWriter(tweet_file,
                                ["type_of_tweet",
                                "id",
                                "author_id",
                                "retweet_id",
                                "text",
                                "retweet_count",
                                "reply_count",
                                "like_count",
                                "withheld",
                                "error"], extrasaction='ignore')

        data_index = {}

        if "data" and "includes" in json_response:

            if "tweets" in json_response["includes"]:

                for tw in json_response["includes"]["tweets"]:

                    for data in json_response["data"]:

                        if "referenced_tweets" in data.keys():

                            #if data['referenced_tweets'][0]["id"]==tw["conversation_id"]:
                            if data['referenced_tweets'][0]["id"]==tw["id"]:

                                if 'public_metrics' in tw:

                                    tw['retweet_count'] = tw["public_metrics"]["retweet_count"]
                                    tw['reply_count'] = tw["public_metrics"]["reply_count"]
                                    tw['like_count'] = tw["public_metrics"]["like_count"]

                                tw["id"]=data['id']
                                tw["retweet_id"]= data["referenced_tweets"][0]["id"]
                                tw["type_of_tweet"]=data["referenced_tweets"][0]["type"]

                                if "withheld" in data.keys():
                                    tw["withheld"]=data["withheld"]["copyright"]

                                writer.writerow(tw)


        elif 'errors' in json_response:
            error = json_response['errors'][0]['title']
            #pass
            tw = {}
            tw['error'] = error
            writer.writerow(tweet)
            print('did not find the tweet')
            print(json_response['errors'][0])


def recollect_tweets_by_id(bearer_token, List_id, file_name):

    filename = os.path.join(".", "data", file_name)

    file_exists = os.path.isfile(file_name)

    with open(filename, "w+") as tweet_file:

        writer = csv.DictWriter(tweet_file,
                                ["type_of_tweet","id", "author_id", "retweet_id", "text",
                                  "retweet_count", "reply_count", "like_count","withheld", "error"], extrasaction='ignore')
        if not file_exists:

            writer.writeheader()

    bearer_token= os.getenv('TWITTER_TOKEN')

    ln=len(List_id)

    #for i in range(0,ln,100):

    #print(i)
        #a=str(List_id[i:i+99])
        #b='ids=' + a[1:-1]
        #ids = 'ids=' + str(List_id[i:i+99]).strip('[]')
        #print(b)
        #ids=b.replace(' ','')
        #ids = b.strip()
        #print(ids)
    url = create_url_recollect('ids=1214598699671834625,1214598423363686401')
    headers = create_headers_recollect(bearer_token)
    json_response = connect_to_endpoint_recollect(url, headers)
    write_results_recollect_tweets(json_response, filename)
        #i+=100
        #sleep(6)
    #     if "errors" in json_response:
    #         #print(json_response["errors"])
    #         errors_name='errors_22_09_2021_2'  + '.csv'
    #
    #         errors = os.path.join(".", "data", errors_name)
    #
    #         file_exists_er = os.path.isfile(errors)


            # with open(errors, "a+") as error_file:
            #     writer = csv.DictWriter(error_file,
            #                     ["resource_type","title", "value", "resource_id" , "detail", "type", "text"], extrasaction='ignore')
            #     if not file_exists_er:
            #         writer.writeheader()
            #
            #     for err in json_response['errors']:
            #         err["resource_type"]=err["resource_type"]
            #         writer.writerow(err)
    #print(json.dumps(json_response, indent=4, sort_keys=True))
