from django.db import models

from base.models import AuditingBase
from tinymce import models as tinymce_models

class Page(AuditingBase):

    # TODO: make unique=True (dependent on migration script)
    guid = models.TextField(blank=True)

    title = models.CharField(max_length=500, blank=True)
    content = tinymce_models.HTMLField()

    # meta information
    page_title = models.CharField(max_length=100, blank=True)
    meta_keywords = models.CharField(max_length=250, blank=True)
    meta_description = models.TextField(blank=True)

    update_dt = models.DateTimeField(auto_now=True)
    create_dt = models.DateTimeField(auto_now_add=True)

    view_contact_form = models.BooleanField()
    design_notes = models.TextField(blank=True)

    syndicate = models.BooleanField()
    displaypagetemplate = models.CharField(max_length=50, blank=True)

    metacanonical = models.TextField(blank=True)
