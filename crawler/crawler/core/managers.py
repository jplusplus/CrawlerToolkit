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

class SubclassingQuerySet(models.query.QuerySet):
    def __getitem__(self, k):
        result = super(SubclassingQuerySet, self).__getitem__(k)
        if isinstance(result, models.Model) :
            return result.as_leaf_class()
        else :
            return result

    def __iter__(self):
        for item in super(SubclassingQuerySet, self).__iter__():
            yield item.as_leaf_class()

class LeafManager(models.Manager):
    def get_queryset(self):
        return SubclassingQuerySet(self.model)

