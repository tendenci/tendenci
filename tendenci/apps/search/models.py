from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class UnindexedItem(models.Model):
    content_type = models.ForeignKey(ContentType, db_index=True)
    object_id = models.PositiveIntegerField()
    create_dt = models.DateTimeField(auto_now_add=True)

    object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        app_label = 'search'
