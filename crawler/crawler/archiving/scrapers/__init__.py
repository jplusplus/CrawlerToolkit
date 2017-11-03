import requests

def detect_notfound(articles):
    not_found = list()
    for article in articles:
        req = requests.get(article.url)
        if req.status is 404:
            not_found.append(article)
    return not_found
