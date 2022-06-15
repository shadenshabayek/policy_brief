# policy_brief_ssk

## Clean data

To create a dataset with links marked as false by continent, then only for EU, run:

```
python3 ./code/clean_dataset.py
```

## Get active Links

To get the active links from the previously created dataset, run:

```
chmod u+x ./code/get_report_condor_EU_false_links.sh
```

```
 ./code/get_report_condor_EU_false_links.sh
```

## Get youtube messages

Run the following, to collect information panels and messages of inactive Youtube videos: 
```
python3 ./code/get_youtube_messages.py
```

## Get tweets 

```
 chmod u+x ./code/collect_tweets_minet.sh
 ```
 
 ```
 ./code/collect_tweets_minet.sh
 ```
 
 ## Create figures
 
 To create all figures run:
 
 ```
python3 ./code/create_figures_tw.py
```

```
python3 ./code/create_figures_yt.py
```

 
