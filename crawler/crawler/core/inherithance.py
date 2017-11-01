from django.db import models
from django.contrib.contenttypes.models import ContentType

class SubclassingQuerySet(models.query.QuerySet):
    def __getitem__(self, k):
        result = super(SubclassingQuerySet, self).__getitem__(k)
        if isinstance(result, models.Model) :
            return result.as_leaf_class()
        else :
            return result

    def __iter__(self):
        for item in super(SubclassingQuerySet, self).__iter__():
            yield item.as_leaf_class()

class LeafManager(models.Manager):
    def get_queryset(self):
        return SubclassingQuerySet(self.model)

class ParentModel(models.Model):
    content_type = models.ForeignKey(ContentType, editable=False, null=True)
    leaf_objects = LeafManager()

    class Meta:
        abstract = False

    def save(self, *args, **kwargs):
        """
        Overrides the default save method from Django. If the method is called for
        a new model, its content type will be saved in the database as well. This way
        it is possible to later determine if the model is an instance of the
        class itself or some of its subclasses.
        """

        if not self.content_type:
            self.content_type = ContentType.objects.get_for_model(self.__class__)

        super(ParentModel, self).save(*args, **kwargs)

    def as_leaf_class(self):
        """
        Checks if the object is an instance of a certain class or one of its subclasses.
        If the instance belongs to a subclass, it will be returned as an instance of
        that class.
        """
        content_type = self.content_type
        model_class = content_type.model_class()
        if (model_class == self.__class__):
            return self
        return model_class.objects.get(id=self.id)
