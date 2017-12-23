from django.db import models
from crawler.utils import pickattr
from crawler.scraping.models import ReleaseDateTag, PriorityTag

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
    def filter_not_needed(self):
        qs = self.get_queryset()
        return qs.exclude(
            archiving_state=STATES.ARCHIVE.ARCHIVED
        ).exclude(
            preservation_state=STATES.PRESERVATION.NO_PRESERVE
        )
    def should_be_archived(self):
        qs = self.get_queryset()
        ids = set(
            ReleaseDateTag.objects.filter(
                article__in=qs,
                value__lte=timezone.now()
            ).values_list('article_id')
        )
        ids = ids.union(
            PriorityTag.objects.filter(
                article__in=qs,
                value=True
            ).values_list('article_id')
        )
        return qs.filter(
            pk__in=list(ids)
        ).exclude(
            archiving_state=STATES.ARCHIVE.ARCHIVED
        )

    def filter_by_tag(self, TagModel):
        qs = self.get_queryset()
        tags = TagModel.objects.filter(article__in=qs).should_preserve()
        return tags.values_list('article')

    def priority_tagged(self):
        return self.filter_by_tag(PriorityTag)

    def release_date_tagged(self):
        return self.filter_by_tag(ReleaseDateTag)

    def not_found_only_tagged(self):
        return self.filter_by_tag(NotFoundOnlyTag)

    def should_be_preserved(self):
        qs = self.get_queryset()
        return list(filter(lambda a: a.should_preserve, qs))
