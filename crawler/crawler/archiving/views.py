from django.shortcuts import render
from crawler.core.models import Article, Feed, HTMLResource
from crawler.constants import STATES
from django.http import HttpResponse, HttpResponseNotFound, FileResponse
ARCHIVING = STATES.ARCHIVE.ARCHIVING

def serve_article(request, feed_slug, article_slug):
    feed = Feed.objects.get(slug=feed_slug)
    article = Article.objects.get(feed=feed, slug=article_slug)
    if article and article.archiving_state == ARCHIVING:
        html_resource = HTMLResource.objects.get(article=article.pk)
        return FileResponse(html_resource.resource_file)
        # html = html_resource.resource_file.read()
        # html_string = html.decode()
        # html_string = html_string.replace('\\n','')
        # import ipdb; ipdb.set_trace()
        # return HttpResponse(html, content_type='text/html')
    else:
        return HttpResponseNotFound()
