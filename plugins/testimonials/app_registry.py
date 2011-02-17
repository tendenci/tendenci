from registry import site
from registry.base import PluginRegistry, lazy_reverse
from models import Testimonial


class TestimonialRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create company testimonials'

site.register(Testimonial, TestimonialRegistry)
