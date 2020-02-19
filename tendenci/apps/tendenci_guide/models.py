from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from tendenci.libs.abstracts.models import OrderingBaseModel

SECTION_CHOICES = (
    ('Events',_('Events')),
    ('Getting Started',_('Getting Started')),
    ('Miscellaneous',_('Miscellaneous')),
)

class Guide(OrderingBaseModel):
    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    content = models.TextField(blank=True)
    section = models.CharField(max_length=50, choices=SECTION_CHOICES, default="misc")

#     class Meta:
#         permissions = (("view_guide",_("Can view guide")),)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('tendenci_guide.guide_page', args=[self.slug])
