import json
import requests
from oauth_hook import OAuthHook


twitter_api_url = 'https://api.twitter.com/1.1'
oauth_hook = OAuthHook(access_token, access_token_secret, consumer_key,
        consumer_secret, oauth_header)

client = requests.session(hooks={'pre_request': oauth_hook})

def scrape(account_name):
    r = client.get((
        '{api_url}{endpoint}?exclude_replies=true&include_rts=true'
        '&screen_name={name}&count={count}'
        ).format(
            endpoint='/statuses/user_timeline.json',
            api_url=twitter_api_url,
            name=account_name,
            count=200
        )
    )

    return urls
