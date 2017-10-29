from .models import Feed, Article

def active_feeds():
    return Feed.objects.active_feeds()


def save_feeds_urls(feeds_urls):
    """
    Save the given feeds_urls and makes sure not to try to save already
    existing url.

    Parameters:
        - feeds_urls, array of urls structured like this [
            [ <feed pk>, <url> ],
            [ <feed pk>, <url> ],
            ...
          ]
    """
    urls = list(map(lambda url: url[1], feeds_urls))
    already_existing_urls = Article.objects.clashing_urls(urls)
    feeds_urls = list(
        filter(lambda url: url[1] not in already_existing_urls,feeds_urls)
    )
    urls_to_create = dict()
    feeds_urls_to_create = list()
    for feed_url in feeds_urls:
        if not urls_to_create.get(feed_url[1], False):
            urls_to_create[feed_url[1]] = True
            feeds_urls_to_create.append(feed_url)

    created = Article.objects.bulk_create(
        map(lambda url: Article(url=url[1], feed_id=url[0]),
            feeds_urls_to_create)
    )
    return created
