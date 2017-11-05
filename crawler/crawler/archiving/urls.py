from django.conf.urls import url
from crawler.archiving import views

urlpatterns = [
    url(r'^(?P<feed_slug>[\w-]+)/(?P<article_slug>[\w-]+)/',
        views.serve_article,
        name='serve_article'),
    url(r'^(?P<feed_slug>[\w-]+)/(?P<article_slug>[\w-]+)/preview',
        views.preview_article,
        name='preview_article'),
]
