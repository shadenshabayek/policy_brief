#!/bin/bash

TODAY_DATE=$(date +"%Y_%m_%d")

minet tw attrition id "./data/tweets_condor_EU_false_links_active_2022_04_04.csv" --user user_id  --ids  > "./data/tweets_condor_EU_false_links_active_2022_04_04_attrition_report.csv"

minet twitter attrition id "./data/tweets_condor_EU_false_links_active_2022_04_04.csv"  -o minet-attrition-report.csv
