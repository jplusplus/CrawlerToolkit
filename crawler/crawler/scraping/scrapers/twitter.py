import json
import requests
from requests_oauthlib import OAuth1
from django.conf import settings

twitter = settings.TWITTER

auth = OAuth1(
    twitter.CONSUMER_KEY, twitter.CONSUMER_SECRET,
    twitter.ACCESS_TOKEN, twitter.ACCESS_SECRET,
)

def only_external_links(urls):
    return filter(lambda url: url.find('twitter.com') < 0, urls)

def scrape(account_url, logger=None):
    account_name = account_url.replace('https://twitter.com/', '')
    # implied multiline string.
    urls = list()
    url  = (
        'https://api.twitter.com/1.1/statuses/user_timeline.json'
        '?exclude_replies=true&include_rts=true'
        '&screen_name={name}&count={count}'
    ).format(name=account_name, count=200)
    req = requests.get(url, auth=auth)
    tweets = req.json()
    for tweet in tweets:
        tweet_urls = tweet['entities']['urls']
        if tweet['retweeted']:
            tweet_urls = tweet['retweeted_status']['entities']['urls']

        urls = urls + list(
            map(lambda url_obj: url_obj['expanded_url'], tweet_urls)
        )

    return only_external_links(urls)
