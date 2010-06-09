from django.db import models

from perms.models import AuditingBaseModel
from pages.managers import PageManager

class Page(AuditingBaseModel):

    # TODO: make unique=True (dependent on migration script)
    guid = models.TextField(blank=True)

    title = models.CharField(max_length=500, blank=True)
    content = models.TextField(blank=True)

    # meta information
    page_title = models.TextField(blank=True)
    meta_keywords = models.TextField(blank=True)
    meta_description = models.TextField(blank=True)

    update_dt = models.DateTimeField(auto_now=True)
    create_dt = models.DateTimeField(auto_now_add=True)

    view_contact_form = models.BooleanField()
    design_notes = models.TextField(blank=True)

    syndicate = models.BooleanField()
    displaypagetemplate = models.CharField(max_length=50, blank=True)

    metacanonical = models.TextField(blank=True)

    objects = PageManager()
    
    class Meta:
        permissions = (("view_page","Can view page"),)

    @models.permalink
    def get_absolute_url(self):
        return ("page", [self.pk])

    def __unicode__(self):
        return self.title
