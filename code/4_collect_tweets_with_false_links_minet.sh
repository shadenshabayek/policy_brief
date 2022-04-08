#!/bin/bash

TODAY_DATE=$(date +"%Y_%m_%d")

minet tw scrape tweets clean_url_256_character "./data/condor_EU_false_links_active_2022_04_04.csv" > "./data/tweets_condor_EU_false_links_active_${TODAY_DATE}.csv"
