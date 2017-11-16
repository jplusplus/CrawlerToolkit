from django.shortcuts import render, redirect
from crawler.core.models import Article, Feed, HTMLResource
from crawler.constants import STATES
from django.http import HttpResponse, HttpResponseNotFound, FileResponse
ARCHIVING = STATES.ARCHIVE.ARCHIVING

def _handle(request, feed_slug, article_slug, preview=False):
    feed = Feed.objects.get(slug=feed_slug)
    article = Article.objects.get(feed=feed, slug=article_slug)
    if article and article.archiving_state == ARCHIVING or preview:
        html_resource = HTMLResource.objects.get(article=article.pk)
        return FileResponse(html_resource.resource_file)
    else:
        return HttpResponseNotFound()

def serve_article(request, feed_slug, article_slug):
    return _handle(request, feed_slug, article_slug)

def preview_article(request, feed_slug, article_slug):
    if request.user.is_authenticated:
        return _handle(request,feed_slug, article_slug, preview=True)
    else:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
