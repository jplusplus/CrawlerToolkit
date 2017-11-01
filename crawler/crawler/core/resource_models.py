from crawler.core import inherithance
from django.db import models

RESOURCE_META_FIELDS = ('upload_to', 'unique_name',)

def add_fields_to_options(options, fields):
    for field in fields:
        if field not in options.DEFAULT_NAMES:
            options.DEFAULT_NAMES = options.DEFAULT_NAMES + (field,)

add_fields_to_options(models.options, RESOURCE_META_FIELDS)

def resource_path(instance, filename):
    meta = instance.as_leaf_class()._meta
    article = instance.article
    feed = article.feed
    folders = [ feed.slug, article.slug ]

    if getattr(meta, 'upload_to'):
        folders.append(getattr(meta, 'upload_to'))

    if getattr(meta, 'unique_name'):
        ext = filename.split('.')[1]
        filename = "%s.$s" % (uuid.uuid4(), ext)

    return "{path}/{fn}".format(
        path='/'.join(folders),
        fn=filename
    )

class Resource(inherithance.ParentModel):
    class Meta:
        unique_name = False

    resource_file = models.FileField(upload_to=resource_path,)
    article = models.ForeignKey('Article', related_name='resources')

class HTMLResource(Resource):pass

class ImageResource(Resource):
    class Meta:
        unique_name = True
        upload_to = 'images'

class ScriptResource(Resource):
    class Meta:
        unique_name = True
        upload_to = 'scripts'

class StyeResource(Resource):
    class Meta:
        unique_name = True
        upload_to = 'styles'
