def trigger_feed_crawl(sender, instance, created=False, *args, **kwargs):
    if created:
        from crawler.core.tasks_utils import crawl_feed
        crawl_feed(instance)


def init():
    from django.db.models.signals import post_save, pre_save
    from crawler.core.models import Feed
    post_save.connect(trigger_feed_crawl, sender=Feed)
