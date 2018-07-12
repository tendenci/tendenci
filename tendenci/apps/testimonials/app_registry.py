from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import AppRegistry
from tendenci.apps.testimonials.models import Testimonial


class TestimonialRegistry(AppRegistry):
    version = '1.0'
    author = 'Tendenci - The Open Source AMS for Associations'
    author_email = 'programmers@tendenci.com'
    description = 'Create company testimonials'

site.register(Testimonial, TestimonialRegistry)
