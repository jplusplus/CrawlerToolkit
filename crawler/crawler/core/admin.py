# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.auth.models import Group
from material.frontend.models import Module
from crawler.core.models import Feed, Article

def force_crawl_feeds(modeladmin, request, queryset):
    from crawler.core.tasks_utils import crawl_feeds
    crawl_feeds(queryset)

def _icon(icon_name): return '<i class="material-icons">%s</i>' % icon_name

@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    actions = [ force_crawl_feeds, ]
    fields = ('active', 'url', 'name')
    list_display = ('name', 'url', 'last_time_crawled')
    readomly_fields = ('last_time_crawled',)
    icon = _icon('rss_feed')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('source','url', 'created_at', 'should_preserve')
    icon = _icon('description')


# Unregister unused models.
admin.site.unregister(Group)
admin.site.unregister(Module)
