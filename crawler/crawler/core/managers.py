from django.db import models

class FeedManager(models.Manager):
    def active_feeds(self):
        return self.get_queryset().filter(active=True)

class ArticleManager(models.Manager):
    def clashing_urls(self, urls):
        formated_urls = "'%s'" % "', '".join(urls)
        raw_rs = self.raw('''
            SELECT id, url FROM core_article WHERE url in (%s);
        ''' % formated_urls)
        return list(
            map(lambda article: article.url, raw_rs)
        )
