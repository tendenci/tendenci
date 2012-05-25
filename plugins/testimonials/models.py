from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from perms.object_perms import ObjectPermission
from tagging.fields import TagField
from perms.models import TendenciBaseModel
from managers import TestimonialManager

class Testimonial(TendenciBaseModel):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=25, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=75, blank=True, null=True)
    company = models.CharField(max_length=75, blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(max_length=255, blank=True, null=True)
    testimonial = models.TextField(help_text=_('Supports &lt;strong&gt;, &lt;em&gt;, and &lt;a&gt; HTML tags.'))
    tags = TagField(blank=True, help_text=_('Tags separated by commas. E.g Tag1, Tag2, Tag3'))

    perms = generic.GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = TestimonialManager()

    def __unicode__(self):
        return '%s, %s' % (self.first_name, self.last_name)

    def first_last_name(self):
        return '%s %s' % (self.first_name, self.last_name)
    
    class Meta:
        permissions = (("view_testimonial","Can view testimonial"),)
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'

    @models.permalink
    def get_absolute_url(self):
        return ("testimonial.view", [self.pk])