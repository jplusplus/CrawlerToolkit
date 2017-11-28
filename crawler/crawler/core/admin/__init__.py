# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group
from django.urls import reverse
from material.frontend.models import Module
from crawler import utils
from crawler.constants import STATES
from crawler.core.models import Feed, Article
from crawler.core.tag_models import *
from crawler.archiving.admin import InlineArchivedArticle
from urllib.parse import urlparse
from django.utils.dateformat import format

from .filters import ShouldPreserveFilter, PreservationTypeFilter
from .actions import force_crawl_articles, force_crawl_feeds

def _icon(icon_name): return '<i class="material-icons">%s</i>' % icon_name

class FeedAdmin(admin.ModelAdmin):
    actions = [ force_crawl_feeds, ]
    fields = ('active', 'url', 'name')
    list_display = ('name', 'url', 'last_time_crawled')
    readonly_fields = ('last_time_crawled',)
    icon = _icon('rss_feed')

admin.site.register(Feed, FeedAdmin)

class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'source',
        'original_url',
        'created_at',
        'get_preservation_state',
        'get_preservation_tags',
        'archiving_state',
        'get_archived_urls'
    )
    list_filter = (
        'feed',
        ShouldPreserveFilter,
        PreservationTypeFilter,
        'preservation_state',
        'archiving_state',
    )

    readonly_fields = ('preview_url', 'url', 'feed', 'crawled_at', 'slug')
    icon = _icon('description')
    inlines = [ InlineArchivedArticle, ]
    actions = [ force_crawl_articles, ]

    def get_queryset(self, request):
        qs = super(ArticleAdmin, self).get_queryset(request)
        qs = qs.prefetch_related(
            'archived_urls',
            'feed'
        )
        return qs

    def original_url(self, obj):
        return '<a href="{href}" target="_blank">{title}</a>'.format(
            href=obj.url,
            title=obj.title,
        )
    original_url.short_description = 'Orignal article'
    original_url.allow_tags = True

    def preview_url(self, obj):
        if obj.preservation_state == STATES.PRESERVATION.STORED:
            preview_url = reverse('store:preview_article', kwargs={
                    'feed_slug':obj.feed.slug,
                    'article_slug':obj.slug,
                })
            return (
                '<a href="{href}" target="_blank" '
                    'class="btn--preview btn wave-effects waves-light z-depth-0">'
                    '<i class="material-icons left">remove_red_eye</i>preview'
                '</a>'
            ).format(
                href=preview_url,
            )
        else:
            return ''

    def get_preservation_state(self, obj):
        state = obj.preservation_state
        label = 'Crawling preservation tags'
        preview = ''
        if state:
            label = STATES.PRESERVATION.label(obj.preservation_state)
            if state == STATES.PRESERVATION.STORED:
                preview = '<br/>' + self.preview_url(obj)
        html = (
            '<div class="text-center">'
                '<span>{label}</span>'
                '{preview}'
            '</div>'
        ).format(label=label, preview=preview)

        return html

    get_preservation_state.allow_tags = True
    get_preservation_state.short_description = 'Preservation State'

    def get_preservation_tags(self, obj):
        def get_tag(tag):
            ttype = preservation_tag_type(tag.__class__)
            print('get_tag %s-%s' % (tag.__class__, ttype))
            ttype = ttype.replace('preservation:', '')
            if tag.is_release_date():
                if tag.value:
                    value = format(tag.value, settings.SHORT_DATETIME_FORMAT)
                else:
                    value = '-'
            else:
                value = tag.value
            return (
                '<div class="chip">'
                    '<span>{type}</span>:&nbsp;'
                    '<b class="bold">{value}</b>'
                '</div>'
            ).format(type=ttype,value=value)
        preservation_tags = obj.preservation_tags()
        if len(preservation_tags) > 0:
            return '&nbsp;'.join(map(get_tag, preservation_tags))
        else:
            if len(obj.preservation_state) > 0:
                return 'No tag detected'
            else:
                return 'Crawling preservation tags'

    get_preservation_tags.allow_tags = True
    get_preservation_tags.short_description = 'Detected tags'

    def get_archived_urls(self, obj):
        def archived_url_to_elem(archived):
            host = urlparse(archived.url).hostname
            return (
                "<div class='chip archived-url'>"
                    "<div class='content'>"
                        "<a href='{url}' target='_blank'>"
                            "{host}"
                        "</a>"
                        "<i class='close material-icons'>link</i>"
                    "</div>"
                "</div>"
            ).format(host=host, url=archived.url)

        urls_elems = map(archived_url_to_elem, obj.archived_urls.all())
        return '&nbsp;'.join(urls_elems)

    get_archived_urls.allow_tags = True
    get_archived_urls.short_description = 'Archived URLs'

admin.site.register(Article, ArticleAdmin)

# Unregister unused models.
admin.site.unregister(Group)
admin.site.unregister(Module)

admin.site.site_title = 'Offshore Journalism Crawler'
