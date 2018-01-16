from django.db import models, transaction
from crawler.constants import STATES
from crawler.archiving.models import ArchivedArticle
from crawler.scraping.models import ReleaseDateTag, PriorityTag, NotFoundOnlyTag
from crawler.utils import pickattr

class ByIdsMixin(object):
    def ids(self, ids):
        if ids:
            return self.get_queryset().filter(pk__in=ids)
        else:
            return self.all()

class FeedManager(models.Manager, ByIdsMixin):
    def active(self):
        return self.get_queryset().filter(active=True)


class ArticleQuerySet(models.query.QuerySet):
    def set_stored(self):
        self.update(preservation_state=STATES.PRESERVATION.STORED)

    def set_archiving(self):
        self.update(archiving_state=STATES.ARCHIVE.ARCHIVING)

    def set_preserving(self):
        self.update(preservation_state=STATES.PRESERVATION.PRESERVING)


    def set_crawled(self):
        with transaction.atomic():
            for article in self:
                article.set_crawled()
                article.save()

    def reset_states(self):
        self.update(
            archiving_state=None,
            preservation_state=''
        )

    def can_be_archived(self):
        return self.exclude(
            archiving_state=STATES.ARCHIVE.ARCHIVED
        ).exclude(
            preservation_state=STATES.PRESERVATION.NO_PRESERVE
        )

    def delete_resources(self):
        return [ a.deletedir() for a in self]

    def tags(self):
        return PriorityTag.objects.filter(
            article__in=self
        ).union(
            ReleaseDateTag.objects.filter(article__in=self)
        ).union(
            NotFoundOnlyTag.objects.filter(article__in=self)
        )

    def delete_tags(self):
        return [ tag.delete() for tag in self.tags() ]

    def archived_urls(self):
        return ArchivedArticle.objects.filter(
            article__in=self
        )

    def delete_archived_urls(self):
        return [ _.delete() for _ in self.archived_urls() ]


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
        tags = TagModel.objects.filter(article__in=self).should_preserve()
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

class ArticleManager(models.Manager, ByIdsMixin):
    def get_queryset(self):
        return ArticleQuerySet(self.model)

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
        # Removing duplicated URLs by creating a dict
        urls_dict = { url[1]: url[0] for url in urls }
        # Convert back to list, it will reverse items tuples order:
        # [ [ pk, url ], ... ] --> [ [ url, pk ], ... ]
        urls = list(urls_dict.items())

        clashing_urls = self.clashing_urls(
            list(map(lambda _: _[0], urls))
        )
        urls_to_create = filter(
            lambda _: _[0] not in clashing_urls,
            urls
        )

        with transaction.atomic():
            created = list(
                map(
                    lambda _: self.create(
                        url=_[0], feed_id=_[1]
                    ),
                    urls_to_create
                )
            )
        return self.ids(pickattr(created, 'pk'))

    def clashing_urls(self, urls):
        formated_urls = "'%s'" % "', '".join(urls)
        raw_rs = self.raw('''
            SELECT id, url FROM core_article WHERE url in (%s);
        ''' % formated_urls)
        return list(
            map(lambda article: article.url, raw_rs)
        )

