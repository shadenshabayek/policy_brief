#!/bin/bash

TODAY_DATE=$(date +"%Y_%m_%d")

minet resolve clean_url "./data/condor_EU_false_links.csv" > "./data/condor_EU_false_links_report_${TODAY_DATE}.csv"
