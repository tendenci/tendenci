from django.db import models
from django.contrib.contenttypes import generic

from tagging.fields import TagField
from perms.models import TendenciBaseModel
from perms.object_perms import ObjectPermission
from quotes.managers import QuoteManager

class Quote(TendenciBaseModel):
    """
    Quotes plugin supports quotes with an author, a source, and the option to add tags
    """
    quote = models.TextField(blank=False)
    author = models.CharField(max_length=200, blank=False)
    source = models.CharField(max_length=200, blank=True, help_text='Original source of the quote')
    tags = TagField(blank=True, help_text='Tag 1, Tag 2, ...')

    perms = generic.GenericRelation(ObjectPermission,
        object_id_field="object_id", content_type_field="content_type")

    objects = QuoteManager()
    
    def __unicode__(self):
        return self.quote
    
    class Meta:
        permissions = (("view_quote","Can view quote"),)
    
    @models.permalink
    def get_absolute_url(self):
        return ("quote.view", [self.pk])