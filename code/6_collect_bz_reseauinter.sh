#!/bin/bash

TODAY_DATE=$(date +"%Y-%m-%d")
OUTPUT_FILE="./data/posts_url_${TODAY_DATE}.csv"

minet bz domain-summary 'reseauinternational.net' --begin-date 2020-01-01 --end-date 2021-01-01 --token BUZZSUMO_TOKEN
minet bz domain 'reseauinternational.net' --begin-date 2020-01-01 --end-date 2021-01-01 --token BUZZSUMO_TOKEN > $OUTPUT_FILE
