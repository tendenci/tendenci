from haystack import indexes
from haystack import site

from models import Testimonial
from perms.indexes import TendenciBaseSearchIndex

class TestimonialIndex(TendenciBaseSearchIndex):
    first_name = indexes.CharField(model_attr='first_name')
    last_name = indexes.CharField(model_attr='last_name')

site.register(Testimonial, TestimonialIndex)
