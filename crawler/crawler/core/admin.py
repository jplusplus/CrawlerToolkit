# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.auth.models import Group
from material.frontend.models import Module
from crawler import utils
from crawler.core.models import Feed, Article
from crawler.core.tag_models import *
from crawler.archiving.admin import InlineArchivedArticle
from urllib.parse import urlparse

def force_crawl_feeds(modeladmin, request, queryset):
    from crawler.core.tasks_utils import crawl_feeds
    crawl_feeds(queryset)

def _icon(icon_name): return '<i class="material-icons">%s</i>' % icon_name

@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    actions = [ force_crawl_feeds, ]
    fields = ('active', 'url', 'name')
    list_display = ('name', 'url', 'last_time_crawled')
    readonly_fields = ('last_time_crawled',)
    icon = _icon('rss_feed')


def force_crawl_articles(modeladmin, request, queryset):
    from crawler.core.tasks_utils import crawl_articles
    crawl_articles(queryset)

class PreservationTypeFilter(admin.SimpleListFilter):
    title = 'Preservation tags detected'
    parameter_name = 'preservation_tags'
    def preservation_tag_model(self, tag_type):
        model = PRESERVATION_TAGS_MAP.get()
        if not model:
            raise ValueError('Tag type not recognized')
    def lookups(self, request, model_admin):
        keywords = (
            (PRESERVATION_TAGS.PRIORITY, 'priority'),
            (PRESERVATION_TAGS.RELEASE_DATE, 'release_date'),
            (PRESERVATION_TAGS.NOT_FOUND_ONLY,'notfound_only')
        )
        return keywords

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            PreservationModel = preservation_tag_model(value)
            tag_qs = PreservationModel.objects.filter(article__in=queryset)
            queryset = queryset.filter(preservation_tags__in=tag_qs)

        return queryset

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'source',
        'url',
        'created_at',
        'should_preserve',
        'preservation_state',
        'archiving_state',
        'archived_urls'
    )
    list_filter = (
        'feed',
        PreservationTypeFilter,
        'preservation_state',
        'archiving_state',
    )
    readonly_fields = ('serve_url', 'url', 'feed', 'crawled_at', 'slug')
    icon = _icon('description')
    actions = [ force_crawl_articles, ]
    inlines = [ InlineArchivedArticle, ]

    def archived_urls(self, obj):
        def archived_url_to_elem(archived):
            host = urlparse(archived.url).hostname
            return (
                "<div class='chip'>"
                    "<a href='{url}' target='_blank'>"
                        "<i class='close material-icons'>link</i>{host}"
                    "</a>"
                "</div>"
            ).format(host=host, url=archived.url)

        urls_elems = map(archived_url_to_elem, obj.archived_urls.all())
        return '&nbsp;'.join(urls_elems)

    archived_urls.allow_tags = True

# Unregister unused models.
admin.site.unregister(Group)
admin.site.unregister(Module)
