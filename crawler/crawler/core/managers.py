from django.db import models

class FeedManager(models.Manager):
    def active_feeds(self):
        return self.get_queryset().filter(active=True)
