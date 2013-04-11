from django.db import models
from django.utils.translation import ugettext_lazy as _

from tendenci.libs.abstracts.models import OrderingBaseModel

SECTION_CHOICES = (
    ('Events','Events'),
    ('Getting Started','Getting Started'),
    ('Miscellaneous','Miscellaneous'),
)

class Guide(OrderingBaseModel):
    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)  
    content = models.TextField(blank=True)
    section = models.CharField(max_length=50, choices=SECTION_CHOICES, default="misc")

    class Meta:
        permissions = (("view_guide","Can view guide"),)

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ("tendenci_guide.guide_page", [self.slug])
