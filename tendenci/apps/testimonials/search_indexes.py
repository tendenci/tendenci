from haystack import indexes
from haystack import site

from tendenci.apps.testimonials.models import Testimonial
from tendenci.core.perms.indexes import TendenciBaseSearchIndex

class TestimonialIndex(TendenciBaseSearchIndex):
    first_name = indexes.CharField(model_attr='first_name')
    last_name = indexes.CharField(model_attr='last_name')

site.register(Testimonial, TestimonialIndex)
