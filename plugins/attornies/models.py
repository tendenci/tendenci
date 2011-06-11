from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.conf import settings

from tagging.fields import TagField
from perms.models import TendenciBaseModel
from files.models import File, file_directory

from attornies.managers import AttorneyManager

CATEGORY_CHOICES = (
    ('SH', 'Shareholder'),
    ('OF', 'Of Counsel'),
    ('AS', 'Associates'),
)

class Photo(File):
    pass

class Attorney(TendenciBaseModel):
    category = models.CharField(_('category'), max_length=2, choices=CATEGORY_CHOICES)
    photo = models.ForeignKey(Photo)
    
    first_name = models.CharField(_('first name'), max_length=36)
    last_name = models.CharField(_('last name'), max_length=36)
    position = models.CharField(_('position'), max_length=36)
    address = models.CharField(_('address'), max_length=200)
    address2 = models.CharField(_('address 2'), max_length=200)
    city = models.CharField(_('city'), max_length=36)
    state = models.CharField(_('state'), max_length=36)
    zip = models.CharField(_('zip'), max_length=8)
    phone = models.CharField(_('phone'), max_length=16)
    fax = models.CharField(_('fax'), max_length=16)
    email = models.EmailField(_('email'))
    bio = models.TextField(_('bio'))
    education = models.TextField(_('bio'))
    casework = models.TextField(_('practice are and casework'))
    admissions = models.TextField(_('admissions'))
    tags = tags = TagField(blank=True, help_text=_('Tags separated by commas. E.g Tag1, Tag2, Tag3'))
    
    objects = AttorneyManager()
    
    class Meta:
        verbose_name = _('Attorney')
        verbose_name_plural = _('Attornies')
        permissions = (("view_attorney","Can view Attorney"),)
    
    @models.permalink
    def get_absolute_url(self):
        return ('attorney.detail', [self.pk])

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)
        
