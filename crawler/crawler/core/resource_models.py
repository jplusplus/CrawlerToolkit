from crawler.core import inherithance
from crawler.constants import RESOURCE_TYPES
from django.db import models
from django.core.files.base import ContentFile
from uuid import uuid4

import re
TXT_RESOURCES_PATTERN = re.compile('.+\.(html|js|css)$')

RESOURCE_META_FIELDS = (
    'resource_type',
)

def add_fields_to_options(options, fields):
    for field in fields:
        if field not in options.DEFAULT_NAMES:
            options.DEFAULT_NAMES = options.DEFAULT_NAMES + (field,)

add_fields_to_options(models.options, RESOURCE_META_FIELDS)

def resource_path(instance, filename):
    article = instance.article
    feed = article.feed
    folders = [ feed.slug, article.slug ]

    if instance.use_resource_type_dir:
        folders.append(
            '{}s'.format(getattr(instance._meta, 'resource_type'))
        )

    if instance.use_unique_name:
        ext = filename.split('.')[-1]
        fid = str(uuid4())
        filename = "{}.{}".format(fid, ext)

    return "{path}/{fn}".format(
        path='/'.join(folders),
        fn=filename
    )


class Resource(inherithance.ParentModel):
    use_resource_type_dir = models.BooleanField(default=True)
    use_unique_name = models.BooleanField(default=True)
    resource_file = models.FileField(max_length=255, upload_to=resource_path,)
    article = models.ForeignKey('Article', related_name='resources')
    url = models.URLField(blank=False, null=False, db_index=True)

    def set_content(self, filename, content):
        self.resource_file.save(filename, ContentFile(content))

class HTMLResource(Resource):
    class Meta:
        resource_type = RESOURCE_TYPES.HTML

class ImageResource(Resource):
    class Meta:
        resource_type = RESOURCE_TYPES.IMAGE

class ScriptResource(Resource):
    class Meta:
        resource_type = RESOURCE_TYPES.SCRIPT

class StyleResource(Resource):
    class Meta:
        resource_type = RESOURCE_TYPES.STYLE

class FontResource(Resource):
    class Meta:
        resource_type = RESOURCE_TYPES.FONT

RESOURCE_TYPES_MAP = {
    RESOURCE_TYPES.SCRIPT:ScriptResource,
    RESOURCE_TYPES.STYLE:StyleResource,
    RESOURCE_TYPES.IMAGE:ImageResource,
    RESOURCE_TYPES.HTML:HTMLResource,
    RESOURCE_TYPES.FONT:FontResource,
}
