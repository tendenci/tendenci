from registry import site
from registry.base import PluginRegistry, lazy_reverse
from tenants.models import Tenant


class TenantRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create tenants type of content'

    url = {
        'add': lazy_reverse('tenants.maps.add'),
        'search': lazy_reverse('tenants.maps'),
        'list': lazy_reverse('tenants.maps'),
    }

site.register(Tenant, TenantRegistry)
