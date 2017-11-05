from django.contrib import admin

from crawler.archiving.models import ArchivedArticle

class InlineArchivedArticle(admin.TabularInline):
    model = ArchivedArticle
    extra = 0
