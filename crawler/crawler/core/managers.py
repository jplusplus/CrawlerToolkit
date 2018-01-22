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
        return self

    def set_archived(self):
        self.update(archiving_state=STATES.ARCHIVE.ARCHIVED)
        return self

    def set_archiving(self):
        self.update(archiving_state=STATES.ARCHIVE.ARCHIVING)
        return self

    def set_preserving(self):
        self.update(preservation_state=STATES.PRESERVATION.PRESERVING)
        return self

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

    def delete_resources(self):
        return [ a.deletedir() for a in self]

    def tags(self):
        qs = list(PriorityTag.objects.filter(
            article__in=self
        ))
        qs = qs + list(
            ReleaseDateTag.objects.filter(article__in=self)
        )
        qs = qs + list(
            NotFoundOnlyTag.objects.filter(article__in=self)
        )
        return qs

    def delete_tags(self):
        return [ tag.delete() for tag in self.tags() ]

    def archived_urls(self):
        return ArchivedArticle.objects.filter(
            article__in=self
        )

    def delete_archived_urls(self):
        return [ _.delete() for _ in self.archived_urls() ]

    def is_not_stored(self):
        return self.exclude(
            preservation_state=STATES.PRESERVATION.STORED
        )

    def should_be_preserved(self):
        # Note: we can't rely on queryset values because should_preserve is a
        # dynamic property.
        return self.filter(pk__in=map(
            lambda a: a.pk,
            filter(lambda a: a.should_preserve, self)
        ))

    def can_be_archived(self):
        return self.exclude(
            archiving_state=STATES.ARCHIVE.ARCHIVED
        ).exclude(
            archiving_state=STATES.ARCHIVE.ARCHIVING
        )

    def should_be_archived(self):
        should_be_archived = self.release_date_tagged(
            should_be_preserved=True
        )
        should_be_archived = should_be_archived.union(
            self.priority_tagged(should_be_preserved=True)
        )
        return should_be_archived

    def filter_by_tag(self, TagModel, should_be_preserved=False):
        tags = TagModel.objects.filter(article__in=self)
        if should_be_preserved:
            tags = tags.should_be_preserved()
        return self.filter(pk__in=tags.values_list('article'))

    def priority_tagged(self, should_be_preserved=False):
        return self.filter_by_tag(PriorityTag, should_be_preserved)

    def release_date_tagged(self, should_be_preserved=False):
        return self.filter_by_tag(ReleaseDateTag, should_be_preserved)

    def not_found_only_tagged(self, should_be_preserved=False):
        return self.filter_by_tag(NotFoundOnlyTag, should_be_preserved)


class ArticleManager(models.Manager, ByIdsMixin):
    def get_queryset(self):
        return ArticleQuerySet(self.model)

    def should_be_preserved(self):
        return self.get_queryset().should_be_preserved()

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

