from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class Meta(models.Model):
    """
    Meta holds meta-information about an object.
    This meta information has to do with html-meta tags,
    such as: title, keyword and description.
    """
    # generic index fields
#    content_type = models.ForeignKey(ContentType)
#    object_id = models.PositiveIntegerField()

    title = models.CharField(max_length=200, blank=True)
    keywords = models.TextField(blank=True)
    description = models.TextField(blank=True)
    canonical_url = models.URLField(max_length=500, blank=True)

    update_dt = models.DateTimeField(auto_now=True)
    create_dt = models.DateTimeField(auto_now_add=True)

#    content_object = generic.GenericForeignKey()

    def __unicode__(self):
        return self.title