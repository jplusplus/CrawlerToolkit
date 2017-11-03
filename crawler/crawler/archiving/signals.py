from django.dispatch import Signal

articles_archived = Signal(providing_args=('articles',))

