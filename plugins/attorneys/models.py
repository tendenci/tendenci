from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.conf import settings
from django.contrib.contenttypes import generic

from perms.object_perms import ObjectPermission
from tagging.fields import TagField
from perms.models import TendenciBaseModel
from files.models import File, file_directory

from attorneys.managers import AttorneyManager

CATEGORY_CHOICES = (
    ('SH', 'Shareholder'),
    ('OF', 'Of Counsel'),
    ('AS', 'Associate'),
)

class Attorney(TendenciBaseModel):
    category = models.CharField(_('category'), max_length=2, choices=CATEGORY_CHOICES)

    first_name = models.CharField(_('first name'), max_length=36)
    middle_initial = models.CharField(_('middle initial'), max_length=36, blank=True)
    last_name = models.CharField(_('last name'), max_length=36)
    slug = models.SlugField(max_length=75, unique=True, default="")
    position = models.CharField(_('position'), max_length=36, blank=True)
    address = models.CharField(_('address'), max_length=200, blank=True)
    address2 = models.CharField(_('address 2'), max_length=200, blank=True)
    city = models.CharField(_('city'), max_length=36, blank=True)
    state = models.CharField(_('state'), max_length=36, blank=True)
    zip = models.CharField(_('zip'), max_length=16, blank=True)
    phone = models.CharField(_('phone'), max_length=36, blank=True)
    fax = models.CharField(_('fax'), max_length=36, blank=True)
    email = models.EmailField(_('email'), blank=True)
    bio = models.TextField(_('bio'), blank=True)
    education = models.TextField(_('education'), blank=True)
    casework = models.TextField(_('practice area and casework'), blank=True)
    admissions = models.TextField(_('admissions'), blank=True)
    ordering = models.IntegerField(blank=True, null=True)
    tags = tags = TagField(blank=True, help_text=_('Tags separated by commas. E.g Tag1, Tag2, Tag3'))
    
    perms = generic.GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = AttorneyManager()

    def __unicode__(self):
        return self.first_name

    def save(self, *args, **kwargs):
        model = self.__class__

        if self.ordering is None:
            # Append
            try:
                last = model.objects.order_by('-ordering')[0]
                self.ordering = last.ordering + 1
            except IndexError:
                # First row
                self.ordering = 0

        return super(Attorney, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Attorney')
        verbose_name_plural = _('Attorneys')
        permissions = (("view_attorney","Can view Attorney"),)
        ordering = ('ordering',)

    @models.permalink
    def get_absolute_url(self):
        return ('attorneys.detail', [self.slug])

    @property
    def name(self):
        if self.middle_initial:   
            return "%s %s. %s" % (self.first_name, self.middle_initial, self.last_name)
        else:
            return "%s %s" % (self.first_name, self.last_name)

    @property
    def category_name(self):
        for cat in CATEGORY_CHOICES:
            if self.category == cat[0]:
                return cat[1]
        return None

    @property
    def photo(self):
        """
        If the need arises we can have multiple photos for attorneys.
        The model can support that.
        For now this method is made assuming that attorney photos are one to one
        with attorneys.
        """
        try:
            return self.photo_set.all()[0]
        except IndexError:
            return None

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)
        
class Photo(File):
    attorney = models.ForeignKey(Attorney)
