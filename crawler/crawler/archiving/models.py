from django.db import models

class ArchivedArticle(models.Model):
    article = models.ForeignKey('core.Article')
    url = models.URLField(blank=False,null=False)
