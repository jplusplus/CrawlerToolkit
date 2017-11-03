from django.dispatch import Signal

articles_crawled = Signal(providing_args=('articles',))
articles_stored  = Signal(providing_args=('articles',))
