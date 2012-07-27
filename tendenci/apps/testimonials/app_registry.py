from tendenci.core.registry import site
from tendenci.core.registry.base import AppRegistry, lazy_reverse
from tendenci.apps.testimonials.models import Testimonial


class TestimonialRegistry(AppRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create company testimonials'

site.register(Testimonial, TestimonialRegistry)
