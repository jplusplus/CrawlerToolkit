from django.db import models

class ArchivedArticle(models.Model):
    article = models.ForeignKey('core.Article', related_name='archived_urls')
    url = models.URLField(blank=False,null=False)
