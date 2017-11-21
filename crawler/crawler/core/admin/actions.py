def force_crawl_articles(modeladmin, request, queryset):
    from crawler.core.tasks_utils import crawl_articles
    crawl_articles(queryset)

def force_crawl_feeds(modeladmin, request, queryset):
    from crawler.core.tasks_utils import crawl_feeds
    crawl_feeds(queryset)
