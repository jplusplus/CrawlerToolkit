import os
import shutil

from django.conf import settings

from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.storage import FileSystemStorage

class StaticStorage(S3Boto3Storage):
    location = getattr(settings, 'STATICFILES_LOCATION', 'static')

class MediaStorage(S3Boto3Storage):
    location = getattr(settings, 'MEDIAFILES_LOCATION', 'media')

    def deletedir(self, path):
        delete_keys = []
        for key in self.bucket.objects.filter(Prefix=path):
            delete_keys.append(key)
        if len(delete_keys) > 0:
            self.bucket.delete_keys(delete_keys)

class LocalMediaStorage(FileSystemStorage):
    # Took from django core files to have the right functionnality
    # https://github.com/django/django/blob/master/django/core/files/storage.py
    def delete(self, name):
        assert name, "The name argument is not allowed to be empty."
        name = self.path(name)
        # If the file or directory exists, delete it from the filesystem.
        try:
            if os.path.isdir(name):
                shutil.rmtree(name)
            else:
                os.remove(name)
        except FileNotFoundError:
            # FileNotFoundError is raised if the file or directory was removed
            # concurrently.
            pass

    def deletedir(self, path):
        return self.delete(path)
