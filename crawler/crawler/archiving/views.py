from django.shortcuts import render
from crawler.core.models import Article, Feed
from crawler.constants import STATES
from django.http import HttpResponse, HttpResponseNotFound
ARCHIVING = STATES.ARCHIVE.ARCHIVING

def serve_article(request, feeld_slug, article_slug):
    feed = Feed.objects.get(slug=feed_slug)
    article = Article.objects.get(feed=feed, slug=article_slug)
    if article and article.archiving_state is ARCHIVING:
        html = article.html_content.read()
        return HttpResponse(html)
    else:
        return HttpResponseNotFound()
