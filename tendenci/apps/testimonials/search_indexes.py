from haystack import indexes

from tendenci.apps.testimonials.models import Testimonial
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex

class TestimonialIndex(TendenciBaseSearchIndex, indexes.Indexable):
    first_name = indexes.CharField(model_attr='first_name')
    last_name = indexes.CharField(model_attr='last_name')
    
    @classmethod
    def get_model(self):
        return Testimonial

