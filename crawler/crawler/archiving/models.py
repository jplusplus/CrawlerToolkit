from django.db import models

class ArchivedArticle(models.Model):
    service = models.CharField(max_length=100, null=False, blank=False)
    article = models.ForeignKey('core.Article', related_name='archived_urls')
    url = models.URLField(blank=False,null=False)
