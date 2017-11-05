from django.shortcuts import render
from crawler.core.models import Article, Feed, HTMLResource
from crawler.constants import STATES
from django.http import HttpResponse, HttpResponseNotFound
ARCHIVING = STATES.ARCHIVE.ARCHIVING

def serve_article(request, feed_slug, article_slug):
    feed = Feed.objects.get(slug=feed_slug)
    article = Article.objects.get(feed=feed, slug=article_slug)
    if article and article.archiving_state == ARCHIVING:
        html_resource = HTMLResource.objects.get(article=article.pk)
        import ipdb; ipdb.set_trace()
        html = html_resource.resource_file.read()
        html_string = html.decode()
        if html_string.startswith('b\''):
            html_string = html_string[2:-1]
        html_string = html_string.replace('\\n','')
        return HttpResponse(html_string.encode('utf-8'))
    else:
        return HttpResponseNotFound()
