import requests

def detect_notfound(articles):
    not_found_ids = list()
    for article in articles:
        req = requests.get(article.url)
        if req.status_code == 404:
            not_found_ids.append(article.pk)
    return articles.filter(pk__in=not_found_ids)
