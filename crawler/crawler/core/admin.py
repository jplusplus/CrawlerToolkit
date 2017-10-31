# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from crawler.core.models import Feed, Article

def force_crawl_feeds(modeladmin, request, queryset):
    from crawler.core.tasks_utils import crawl_feeds
    crawl_feeds(queryset)

@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    actions = [ force_crawl_feeds, ]
    fields = ('active', 'url', 'name')
    list_display = ('name', 'url', 'last_time_crawled')
    readomly_fields = ('last_time_crawled',)
    icon = '<i class="material-icons">rss_feed</i>'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('source','url', 'created_at', 'should_preserve')


