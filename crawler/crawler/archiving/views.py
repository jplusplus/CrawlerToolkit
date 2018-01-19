from django.shortcuts import render, redirect
from django.conf import settings
from crawler.core.models import Article, Feed
from crawler.constants import STATES

from django.http import HttpResponseForbidden, HttpResponseNotFound, FileResponse
ARCHIVING = STATES.ARCHIVE.ARCHIVING

def _handle(request, feed_slug, article_slug, preview=False):
    feed = Feed.objects.get(slug=feed_slug)
    article = Article.objects.get(feed=feed, slug=article_slug)
    found_article = article and article.has_index_resource()
    can_see = article.archiving_state == ARCHIVING or preview
    if found_article:
        if can_see:
            return FileResponse(article.index_resource())
        else:
            return HttpResponseForbidden()
    else:
        return HttpResponseNotFound()

def serve_article(request, feed_slug, article_slug):
    return _handle(request, feed_slug, article_slug)

def preview_article(request, feed_slug, article_slug):
    if request.user.is_authenticated:
        return _handle(request,feed_slug, article_slug, preview=True)
    else:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
