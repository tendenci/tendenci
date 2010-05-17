from django.db import models

from base.models import AuditingBase

class Page(AuditingBase):

    # TODO: make unique=True (dependent on migration script)
    guid = models.TextField(blank=True)

    title = models.CharField(max_length=500, blank=True)
    content = models.TextField(blank=True)

    # meta information
    page_title = models.TextField(blank=True)
    meta_keywords = models.TextField(blank=True)
    meta_description = models.TextField(blank=True)

    # might go away w/ permissions
    allow_anonymous_view = models.BooleanField()
    allow_site_user_view = models.BooleanField()
    allow_member_view = models.BooleanField()
    allow_anonymous_edit = models.BooleanField()
    allow_site_user_edit = models.BooleanField()
    allow_member_edit = models.BooleanField()

    update_dt = models.DateTimeField(auto_now=True)
    create_dt = models.DateTimeField(auto_now_add=True)

    design_notes = models.TextField(blank=True)

    syndicate = models.BooleanField()
    displaypagetemplate = models.CharField(max_length=50, blank=True)

    metacanonical = models.TextField(blank=True)
