from crawler.utils import pickattr

def force_crawl_articles(modeladmin, request, queryset):
    from crawler.scraping.tasks import crawl_articles
    crawl_articles.delay(
        ids=pickattr(queryset, 'pk'),
        update=True
    )

def force_crawl_feeds(modeladmin, request, queryset):
    from crawler.scraping.tasks import crawl_feeds
    crawl_feeds.delay(
        ids=pickattr(queryset, 'pk')
    )

