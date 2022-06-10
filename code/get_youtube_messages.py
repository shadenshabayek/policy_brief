import csv
import pandas as pd
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from utils import import_data
from webdriver_manager.chrome import ChromeDriverManager

def get_inactive_video_message(video_id):

    browser = webdriver.Chrome(ChromeDriverManager().install())
    browser.get('https://www.youtube.com/watch?v=' + video_id)
    time.sleep(10)

    try:
        unavailable_video_message = browser.find_element_by_xpath('//*[@id="contents"]').text
    except NoSuchElementException:
        unavailable_video_message = ''

    try:
        removed_video_message = browser.find_element_by_xpath('//*[@id="reason"]').text
    except NoSuchElementException:
        removed_video_message = ''

    try:
        information_panel_content = browser.find_element_by_xpath('//*[@id="clarify-box"]').text
    except NoSuchElementException:
        information_panel_content = ''

    browser.quit()

    # print(unavailable_video_message)
    # print(removed_video_message)
    # print(information_panel_content)

    return unavailable_video_message, removed_video_message, information_panel_content

def get_videos():

    df = import_data('videos_youtube_condor_EU_false_links_active_2022-04-04.csv')
    df['video_id'] = df['video_id'].fillna('not found')

    list_video_id = df['yt_video_id'].tolist()
    list_url = df['clean_url'].tolist()
    list_published_at = df['published_at'].tolist()
    list_title = df['title'].tolist()

    return list_video_id, list_url, list_published_at, list_title

def collect_messages():

    list_video_id, list_url, list_published_at, list_title = get_videos()

    with open('./data/messages_videos_youtube_condor_EU_false_links_active_2022_04_04.csv', 'w+') as csv_file:

        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(['video_id',
                         'not_found_message',
                         'suspended_message',
                         'information_panel',
                         'clean_url',
                         'published_at',
                         'title'])

        l = len(list_video_id)
        for i in range(0,l):
            a, b, c = get_inactive_video_message(list_video_id[i])
            writer.writerow([list_video_id[i],
                             a,
                             b,
                             c,
                             list_url[i],
                             list_published_at[i],
                             list_title[i]])

if __name__ == '__main__':

    collect_messages()
