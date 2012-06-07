from registry import site
from registry.base import PluginRegistry, lazy_reverse
from products.models import Product


class ProductRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create products type of content'

site.register(Product, ProductRegistry)
