#!/bin/bash

TODAY_DATE=$(date +"%Y-%m-%d")
INPUT_FILE="./data/youtube_condor_EU_false_links_active.csv"
OUTPUT_FILE="./data/videos_youtube_condor_EU_false_links_active_${TODAY_DATE}.csv"

minet youtube videos yt_video_id $INPUT_FILE --key YOUTUBE_TOKEN > $OUTPUT_FILE
