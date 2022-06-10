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
    plt.savefig(figure_path, bbox_inches='tight', dpi=1000)
    print('The {} figure is saved.'.format(figure_name))

def save_data(df, file_name, append):

    file_path = os.path.join('.', 'data', file_name)

    if append == 1:
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(file_path, index=False)

    print(' {} is saved.'.format(file_name))

"Tweet search"

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

"historical search"

def connect_to_endpoint_historical_search(bearer_token, query, start_time, end_time, next_token=None):

    max_results=100

    headers = {'Authorization': 'Bearer {}'.format(bearer_token)}

    params = {'tweet.fields' : 'in_reply_to_user_id,author_id,context_annotations,created_at,public_metrics,entities,geo,id,possibly_sensitive,lang,referenced_tweets', 'user.fields':'username,name,description,location,created_at,entities,public_metrics','expansions':'author_id,referenced_tweets.id,attachments.media_keys'}

    if (next_token is not None):
        url = 'https://api.twitter.com/2/tweets/search/all?max_results={}&query={}&start_time={}&end_time={}&next_token={}'.format(max_results, query, start_time, end_time, next_token)
    else:
        url = 'https://api.twitter.com/2/tweets/search/all?max_results={}&start_time={}&end_time={}&query={}'.format(max_results, start_time, end_time, query)

    with requests.request('GET', url, params=params, headers=headers) as response:

        if response.status_code != 200:
            raise Exception(response.status_code, response.text)

        return response.json()

def write_results(json_response, filename, query):

    with open(filename, "a+") as tweet_file:

        writer = csv.DictWriter(tweet_file,
                                ["query",
                                "type_of_tweet",
                                "referenced_tweet_id",
                                 "id",
                                 "author_id",
                                 "username",
                                 "name",
                                 "created_at",
                                 "text",
                                 "possibly_sensitive",
                                 "retweet_count",
                                 "reply_count",
                                 "like_count",
                                 "hashtags",
                                 "in_reply_to_user_id",
                                 "in_reply_to_username",
                                 "quoted_user_id",
                                 "quoted_username",
                                 "retweeted_username",
                                 "mentions_username",
                                 "lang",
                                 "expanded_urls",
                                 "domain_name",
                                 "user_created_at",
                                 "user_profile_description",
                                 "user_location",
                                 "followers_count",
                                 "following_count",
                                 "tweet_count",
                                 "listed_count",
                                 "collection_date",
                                 "collection_method",
                                 'errors',
                                 'error_type'],
                                extrasaction='ignore')

        if 'data' and 'includes' in json_response:
            for tweet in json_response['data']:

                user_index = {}

                for user in json_response['includes']['users']:

                    if 'id' in user.keys():

                        user_index[user['id']] = user

                        if tweet['author_id'] == user['id']:

                            tweet['username'] = user['username']
                            tweet['name'] = user['name']
                            tweet['user_created_at'] = user['created_at']
                            tweet['followers_count'] = user['public_metrics']['followers_count']
                            tweet['following_count'] = user['public_metrics']['following_count']
                            tweet['tweet_count'] = user['public_metrics']['tweet_count']
                            tweet['listed_count'] = user['public_metrics']['listed_count']

                            if 'description' in user.keys():
                                tweet['user_profile_description']= user ['description']

                            if "location" in user.keys():
                                tweet['user_location'] = user['location']

                        if 'in_reply_to_user_id' in tweet.keys():

                            if tweet['in_reply_to_user_id'] == user['id']:

                                a = user['username'].lower()
                                #print('in reply', a)

                                tweet['in_reply_to_username'] = a

                if "context_annotations" in tweet:
                    if "domain" in tweet["context_annotations"][0]:
                        tweet['theme']=tweet["context_annotations"][0]["domain"]["name"]
                        if "description" in tweet["context_annotations"][0]["domain"]:
                            tweet['theme_description']=tweet["context_annotations"][0]["domain"]['description']
                    else:
                        tweet['theme']=''
                        tweet['theme_description']=''

                if "entities" in tweet:

                    if "mentions" in tweet["entities"]:

                        l=len(tweet["entities"]['mentions'])

                        tweet['mentions_username'] = []

                        for i in range(0,l):

                            a = tweet["entities"]['mentions'][i]['username']
                            a = a.lower()
                            tweet['mentions_username'].append(a)

                    else:
                        tweet['mentions_username'] = []

                    if "urls" in tweet["entities"]:

                        lu=len(tweet["entities"]['urls'])

                        tweet['expanded_urls']=[]
                        tweet['domain_name']=[]

                        for i in range(0,lu):

                            link = tweet["entities"]['urls'][i]['expanded_url']
                            #print (i,tweet["entities"]['urls'][i].keys())

                            # if tweet['id'] == "1455491668728328192":
                            #     print(json_response['data'])

                            if len(link) < 35:

                                if 'unwound_url' in tweet["entities"]['urls'][i].keys():
                                    b = tweet["entities"]['urls'][i]['unwound_url']
                                    c = get_domain_name(tweet["entities"]['urls'][i]['unwound_url'])

                                elif 'unwound_url' not in tweet["entities"]['urls'][i].keys():
                                    #print('unwound not there!')
                                    #print(tweet['id'])
                                    for result in multithreaded_resolve([link]):
                                        b = result.stack[-1].url
                                        c = get_domain_name(result.stack[-1].url)

                                # tweet['expanded_urls'].append(b)
                                # tweet['domain_name'].append(c)
                                    # tweet['expanded_urls'].append(b)
                                    # tweet['domain_name'].append(c)

                                else:
                                    b = tweet["entities"]['urls'][i]['expanded_url']
                                    c = get_domain_name(tweet["entities"]['urls'][i]['expanded_url'])

                                tweet['expanded_urls'].append(b)
                                tweet['domain_name'].append(c)


                            else:
                                d = tweet["entities"]['urls'][i]['expanded_url']
                                e = get_domain_name(tweet["entities"]['urls'][i]['expanded_url'])

                                tweet['expanded_urls'].append(d)
                                tweet['domain_name'].append(e)
                    else:
                        tweet['expanded_urls'] = []
                        tweet['domain_name'] = []

                    if "hashtags" in tweet["entities"]:
                        l=len(tweet["entities"]["hashtags"])
                        tweet["hashtags"] = []

                        for i in range(0,l):
                            a = tweet["entities"]["hashtags"][i]["tag"]
                            tweet["hashtags"].append(a)
                    else:
                        tweet["hashtags"] = []
                else:
                    tweet['mentions_username'] = []
                    tweet['hashtags'] = []
                    tweet['expanded_urls'] = []
                    tweet['domain_name'] = []

                if "referenced_tweets" in tweet.keys():

                    tweet["type_of_tweet"] = tweet["referenced_tweets"][0]["type"]
                    tweet["referenced_tweet_id"] = tweet["referenced_tweets"][0]["id"]

                    if (tweet["referenced_tweets"][0]["type"] == "retweeted" or tweet["referenced_tweets"][0]["type"] == "quoted" or tweet["referenced_tweets"][0]["type"] == "replied_to"):

                        if "tweets" in json_response["includes"]:

                            for tw in json_response["includes"]["tweets"]:

                                if tweet["referenced_tweets"][0]["id"] == tw["id"] :

                                    tweet['retweet_count'] = tw["public_metrics"]["retweet_count"]
                                    tweet['reply_count'] = tw["public_metrics"]["reply_count"]
                                    tweet['like_count'] = tw["public_metrics"]["like_count"]
                                    tweet['possibly_sensitive'] = tw['possibly_sensitive']
                                    tweet['text'] = tw['text']

                                    if tweet['referenced_tweets'][0]['type'] == 'retweeted':

                                        if 'entities' in tweet :

                                            if 'mentions' in tweet['entities'].keys():

                                                if tweet['entities']['mentions'][0]['id'] == tw['author_id'] :

                                                    a = tweet['entities']['mentions'][0]['username']
                                                    b = a.lower()

                                                    tweet['retweeted_username'] = b

                                    if tweet['referenced_tweets'][0]['type'] == 'replied_to':

                                        if 'entities' in tweet :

                                            if 'mentions' in tweet['entities'].keys():

                                                if tweet['entities']['mentions'][0]['id'] == tweet['in_reply_to_user_id'] :

                                                    a = tweet['entities']['mentions'][0]['username']
                                                    b = a.lower()

                                                    tweet['in_reply_to_username'] = b


                                    if tweet['referenced_tweets'][0]['type'] == 'quoted':

                                        tweet['quoted_user_id'] = tw['author_id']

                                        if 'entities' in tweet.keys():

                                            if 'urls' in tweet['entities']:

                                                l = len(tweet['entities']['urls'])

                                                for i in range(0,l):

                                                    if 'expanded_url' in tweet['entities']['urls'][i].keys():

                                                        url = tweet['entities']['urls'][i]['expanded_url']

                                                        if tweet['referenced_tweets'][0]['id'] in url:

                                                            #sprint(tweet['entities']['urls'][0]['expanded_url'])
                                                            if 'https://twitter.com/' in url:

                                                                a = url.split('https://twitter.com/')[1]
                                                                b = a.split('/status')[0].lower()

                                                                tweet['quoted_username'] = b

                                    if 'entities' in  tw.keys():

                                        if "urls" in tw["entities"]:

                                            lu=len(tw["entities"]['urls'])

                                            tweet['expanded_urls']=[]
                                            tweet['domain_name']=[]

                                            for i in range(0,lu):

                                                link = tw["entities"]['urls'][i]['expanded_url']

                                                if len(link) < 35:

                                                    if 'unwound_url' in tw["entities"]['urls'][i].keys():
                                                        b = tw["entities"]['urls'][i]['unwound_url']
                                                        c = get_domain_name(tw["entities"]['urls'][i]['unwound_url'])

                                                    elif 'unwound_url' not in tw["entities"]['urls'][i].keys():
                                                        for result in multithreaded_resolve([link]):
                                                            b = result.stack[-1].url
                                                            c = get_domain_name(result.stack[-1].url)

                                                    #tweet['expanded_urls'].append(b)
                                                    #tweet['domain_name'].append(c)


                                                        # tweet['expanded_urls'].append(b)
                                                        # tweet['domain_name'].append(c)

                                                    else:
                                                        b = tw["entities"]['urls'][i]['expanded_url']
                                                        c = get_domain_name(tw["entities"]['urls'][i]['expanded_url'])

                                                    tweet['expanded_urls'].append(b)
                                                    tweet['domain_name'].append(c)

                                                else:
                                                    d = tw["entities"]['urls'][i]['expanded_url']
                                                    e = get_domain_name(tw["entities"]['urls'][i]['expanded_url'])

                                                    tweet['expanded_urls'].append(d)
                                                    tweet['domain_name'].append(e)

                                        else:
                                            tweet['expanded_urls'] = []
                                            tweet['domain_name'] = []

                                        if "hashtags" in tw["entities"]:
                                            l=len(tw["entities"]["hashtags"])
                                            tweet["hashtags"] = []

                                            for i in range(0,l):
                                                a = tw["entities"]["hashtags"][i]["tag"]
                                                tweet["hashtags"].append(a)
                                        else:
                                            tweet["hashtags"] = []

                                        if "mentions" in tw["entities"]:

                                            l=len(tw["entities"]['mentions'])
                                            #tweet['mentions_username'] = []

                                            for i in range(0,l):
                                                a = tw["entities"]['mentions'][i]['username']
                                                a = a.lower()
                                                tweet['mentions_username'].append(a)


                else:

                    tweet['retweet_count'] = tweet["public_metrics"]["retweet_count"]
                    tweet['reply_count'] = tweet["public_metrics"]["reply_count"]
                    tweet['like_count'] = tweet["public_metrics"]["like_count"]

                tweet["query"] = query
                tweet["username"] = tweet["username"].lower()


                if len(tweet["mentions_username"]) > 1:
                    tweet["mentions_username"] = list(set(tweet["mentions_username"]))

                timestr = time.strftime("%Y-%m-%d")
                tweet["collection_date"] = timestr
                tweet["collection_method"] = 'Twitter API V2'

                if 'errors' in json_response:
                    for error in json_response['errors']:
                        if "referenced_tweets" in tweet.keys():
                            if tweet["referenced_tweets"][0]["id"] == error['resource_id']:
                                tweet['errors'] = error['detail']
                                tweet['error_type'] = error['title']

                writer.writerow(tweet)

        else:
            #raise ValueError("User not found")
            pass

def get_next_token(query, token, count, filename, start_time, end_time, bearer_token):

    json_response = connect_to_endpoint_historical_search(bearer_token, query, start_time, end_time, token)

    result_count = json_response['meta']['result_count']

    if 'next_token' in json_response['meta']:
        sleep(3)
        next_token = json_response['meta']['next_token']
        if result_count is not None and result_count > 0:

            count += result_count
            print(count)
        #try:
        write_results(json_response, filename, query)
        return next_token, count
    else:
        write_results(json_response, filename, query)
        return None, count

def collect_twitter_data(query, start_time, end_time, bearer_token, filename):

    print(query)

    flag = True
    count = 0
    file_exists = os.path.isfile(filename)

    with open(filename, "a+") as tweet_file:

        writer = csv.DictWriter(tweet_file,
                                ["query",
                                "type_of_tweet",
                                "referenced_tweet_id",
                                 "id",
                                 "author_id",
                                 "username",
                                 "name",
                                 "created_at",
                                 "text",
                                 "possibly_sensitive",
                                 "retweet_count",
                                 "reply_count",
                                 "like_count",
                                 "hashtags",
                                 "in_reply_to_user_id",
                                 "in_reply_to_username",
                                 "quoted_user_id",
                                 'quoted_username',
                                 "retweeted_username",
                                 "mentions_username",
                                 "lang",
                                 "expanded_urls",
                                 "domain_name",
                                 "user_created_at",
                                 "user_profile_description",
                                 "user_location",
                                 "followers_count",
                                 "following_count",
                                 "tweet_count",
                                 "listed_count",
                                 "collection_date",
                                 "collection_method",
                                 'errors',
                                 'error_type'], extrasaction='ignore')
        if not file_exists:
            writer.writeheader()

    next_token = None

    while flag:
        next_token, count = get_next_token(query, next_token, count, filename, start_time, end_time, bearer_token)
        if count >= 2000000:
            break
        if next_token is None:
            flag = False


    print("Total Tweet IDs saved: {}".format(count))
