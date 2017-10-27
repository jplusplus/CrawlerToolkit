# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from crawler.core.models import Feed

feed_fields = ['active']
readonly_feed_fields = ('last_time_crawled', )


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    fields = ('active', 'url')
    readomly_fields = ('last_time_crawled',)


