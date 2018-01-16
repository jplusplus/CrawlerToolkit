from django.db import models
from crawler.utils import pickattr
from crawler.scraping.models import ReleaseDateTag, PriorityTag, NotFoundOnlyTag
from crawler.constants import STATES

class ByIdsMixin(object):
    def ids(self, ids):
        return self.get_queryset().filter(pk__in=ids)

class FeedManager(models.Manager, ByIdsMixin):
    def active(self):
        return self.get_queryset().filter(active=True)

class ArticleManager(models.Manager, ByIdsMixin):
    def save_urls(self, urls):
        """
        Save the given articles_urls and makes sure not to try to save already
        existing url.

        Parameters:
            - articles_urls, array of urls structured like this [
                [ <feed pk>, <url> ],
                [ <feed pk>, <url> ],
                ...
              ]
        """
        clashing_urls = self.clashing_urls(
            list(map(lambda _: _[1], urls))
        )
 
        with transaction.atomic():
            created = list(
                map(
                    lambda _: self.create(
                        url=_[1], feed_id=_[0]
                    ), filter(
                        lambda _: _[1] not in clashing_urls,
                        urls
                    )
                )
            )
        return created

    def clashing_urls(self, urls):
        formated_urls = "'%s'" % "', '".join(urls)
        raw_rs = self.raw('''
            SELECT id, url FROM core_article WHERE url in (%s);
        ''' % formated_urls)
        return list(
            map(lambda article: article.url, raw_rs)
        )

    def set_crawled(self):
        for article in self.get_queryset():
            article.crawled_at = timezone.now()
            if not article.should_preserve:
                article.preservation_state = STATES.PRESERVATION.NO_PRESERVE
            elif article.preservation_state is not STATES.PRESERVATION.STORED:
                article.preservation_state = STATES.PRESERVATION.PRESERVE
            article.save()

    def reset_states(self):
        self.get_queryset().update(
            archiving_state=None,
            preservation_state=''
        )

    def delete_resources(self):
        return [ a.deletedir() for a in self.get_queryset()]

    def delete_tags(self):
        qs = self.get_queryset()
        tags = PriorityTag.objects.filter(
            article__in=qs
        ).union(
            ReleaseDateTag.objects.filter(article__in=qs)
        ).union(
            NotFoundOnlyTag.objects.filter(article__in=qs)
        )

        return [ tag.delete() for tag in tags ]

    def delete_archived_urls(self):
        from crawler.archiving.models import ArchivedArticle
        archived_articles = ArchivedArticle.objects.filter(
            article__in=self.get_queryset()
        )
        return [ _.delete() for _ in archived_articles]

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

    def set_preserving(self):
        self.update(preservation_state=STATES.PRESERVATION.PRESERVING)

    def should_be_preserved(self):
        qs = self.get_queryset()
        return list(filter(lambda a: a.should_preserve, qs))
