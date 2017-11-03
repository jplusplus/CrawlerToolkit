"""
Signals receivers
"""
from crawler.core import tasks_utils

def trigger_feed_crawl(sender, instance, created=False, *args, **kwargs):
    if created:
        tasks_utils.crawl_feed(instance)

def delete_resource_file(sender, instance, *args, **kwargs):
    instance.resource_file.delete(save=False)

def init():
    from django.db.models.signals import post_save, post_delete
    from crawler.core.models import Feed, Resource
    post_delete.connect(delete_resource_file, sender=Resource)
    post_save.connect(trigger_feed_crawl, sender=Feed)
