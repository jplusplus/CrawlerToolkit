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
            """
            if len(delete_keys) > 100:
                self.bucket.delete_keys(delete_keys)
                delete_keys = []
            """
        print('keys to delete %s' % delete_keys)
        """
        if len(delete) > 0:
            self.bucket.delete_keys(delete_keys)
        """

class LocalMediaStorage(FileSystemStorage):
    def deletedir(self, path):
        pass
