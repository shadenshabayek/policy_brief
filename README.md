# policy_brief_ssk

## Clean data

To create a dataset with links marked as false by continent, then only for EU, run:

```
python3 ./code/1_clean_dataset.py
```

## Get active Links

To get the active links from the previously created dataset, run:

```
chmod u+x ./code/2_get_report_condor_EU_false_links.sh
```

```
./code/2_get_report_condor_EU_false_links.sh
```

## Investigate active links

Run the following, to only keep the active links with status 200 and get a separate file for youtube videos: 
```
./code/3_investigate_active_links.py
```

## Get tweets containing active links 

```
 chmod u+x ./code/4_collect_tweets_with_false_links_minet.sh
 ```
 
 ```
 ./code/4_collect_tweets_with_false_links_minet.sh
 ```
