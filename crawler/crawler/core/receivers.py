"""
Signals receivers
"""

def trigger_feed_crawl(sender, instance, created=False, *args, **kwargs):
    from crawler.scraping.tasks import crawl_feeds
    if created:
        crawl_feeds.delay([instance.pk])

def delete_resources(sender, instance, *args, **kwargs):
    instance.deletedir()

def init():
    from django.db.models.signals import post_save, post_delete
    from crawler.core.models import Feed, Article
    post_delete.connect(delete_resources, sender=Article)
    post_save.connect(trigger_feed_crawl, sender=Feed)
