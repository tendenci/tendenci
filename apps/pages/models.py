import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from tagging.fields import TagField
from perms.models import TendenciBaseModel
from pages.managers import PageManager
from tinymce import models as tinymce_models

class Page(TendenciBaseModel):
    guid = models.CharField(max_length=40, default=uuid.uuid1)
    title = models.CharField(max_length=500, blank=True)
    content = tinymce_models.HTMLField()
    view_contact_form = models.BooleanField()
    design_notes = models.TextField(_('Design Notes'), blank=True)
    syndicate = models.BooleanField(_('Include in RSS feed'))
    template = models.CharField(_('Template'), max_length=50, blank=True)
    tags = TagField(blank=True)
    objects = PageManager()

    class Meta:
        permissions = (("view_page","Can view page"),)

    @models.permalink
    def get_absolute_url(self):
        return ("page", [self.pk])

    def __unicode__(self):
        return self.title
