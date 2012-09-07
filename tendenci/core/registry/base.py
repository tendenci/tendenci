from django.core.urlresolvers import reverse
from django.utils.functional import lazy
from django.contrib.admin import site as admin_site
from django.utils.translation import ugettext_lazy as _

from tendenci.core.registry.exceptions import *

lazy_reverse = lazy(reverse, str)


class FieldDict(dict):
    """
    Custom Field dict that will allow unicode
    representation based on a models verbose_name
    """
    def __unicode__(self):
        return self['verbose_name_plural'].lower()


class DeclarativeMetaclass(type):
    """
    Metaclass for app registry

    Loops through available fields and assigns them to
    a FieldDict to be used in templates or python code
    """
    def __new__(cls, name, bases, attrs):
        attrs['fields'] = FieldDict()
        allowed_fields = [
            '__doc__',
            'version',
            'author',
            'author_email',
            'description',
            'icon',
            'url',
            'packages',
            'event_logs'
        ]

        if 'app_registry' in attrs['__module__']:
            for field_name, item in attrs.items():
                if field_name not in ['fields', '__module__']:
                    if field_name not in allowed_fields:
                        exception = 'Registry field %s not allowed. '\
                                    'The following fields are allowed: %s'
                        raise FieldNotAllowed(_(exception) % (
                            field_name,
                            allowed_fields
                        ))
                    field = attrs.pop(field_name)
                    attrs['fields'][field_name] = field

        return super(DeclarativeMetaclass, cls).__new__(cls, name, bases, attrs)


class Registry(object):
    """
    Base registry class for core and plugin applications

    Example Registry:

    from tendenci.core.registry import site
    from tendenci.core.registry.base import CoreRegistry, lazy_reverse
    from tendenci.addons.models import ExmpleModel

    class ExampleRegistry(CoreRegistry):
        version = '1.0'
        author = 'Glen Zangirolami'
        author_email = 'glenbot@gmail.com'
        description = 'Create staff pages easily with photo, position, bio and more ..'

        url = {
            'add': lazy_reverse('page.add'),
            'search': lazy_reverse('page.search'),
        }

    site.register(ExampleModel, ExampleRegistry)
    """
    __metaclass__ = DeclarativeMetaclass

    def __init__(self, model):
        self.model = model
        self.has_admin = self._has_admin()

        # provide the model in case extra parameters are needed
        self.fields['model'] = self.model

        # transfer verbose names for easy access
        self.fields['verbose_name'] = unicode(self.model._meta.verbose_name)
        self.fields['verbose_name_plural'] = unicode(self.model._meta.verbose_name_plural)

        # default url patterns
        if 'url' not in self.fields:
            self.fields['url'] = self._get_url()

        # default icon path
        if 'icon' not in self.fields:
            self.fields['icon'] = self._get_icon()

        if 'packages' in self.fields:
            if not isinstance(self.fields['packages'], tuple):
                raise FieldError(_('Registry field packages must be of type tuple'))
            self._test_packages(self.fields['packages'])

    def _test_packages(self, packages):
        """
        Attempts to import the packages listed in the plugin registry
        Raises an error if the package cannot be imported
        """
        for package in packages:
            try:
                __import__(package)
            except:
                exception = 'Plugin dependency package `%(package)s` could not be imported. ' \
                            'Try `pip install %(package)s`?'
                raise PackageImportError(_(exception) % {
                    'package': package,
                })

    def _get_icon(self):
        """
        Autogenerate the location for the apps icon
        """
        # TODO: find a more global area to set this URL path
        default_plugin_url = 'plugin-media'
        return '/%s/%s/images/icon.png' % (
            default_plugin_url,
            unicode(self.model._meta.verbose_name_plural.lower())
        )

    def _get_url(self):
        """
        Autogenetate the URLs that will exist in the apps urls dict

        Example from template::

            {{ app.url.add }}
            {{ app.url.search }}
            {{ app.url.list }}

        Example in python::

            app['url']['add']
            app['url']['search']
            app['url']['list']
        """
        url = {
            'add': '',
            'search': '',
            'list': '',
        }
        admin_add = 'admin:%s_%s_add' % (
            self.model._meta.app_label,
            self.model._meta.module_name,
        )
        admin_index = 'admin:%s_%s_changelist' % (
            self.model._meta.app_label,
            self.model._meta.module_name,
        )
        if self.has_admin:
            url.update({
                'add': self._reverse(admin_add),
                'search': self._reverse(admin_index),
                'list': self._reverse(admin_index)
            })
        return url

    def _has_admin(self):
        """
        Tests for django admin site registration
        """
        for model in admin_site._registry.keys():
            if self.model is model:
                return True
        return False

    def _reverse(self, namespace):
        """
        Lazy url resolver
        """
        return lazy_reverse(namespace)


class CoreRegistry(Registry):
    """
    Registry for core applications
    """
    def __init__(self, model):
        super(CoreRegistry, self).__init__(model)

        # application type
        self.fields['app_type'] = 'core'


class AppRegistry(Registry):
    """
    Registry for addon applications
    """
    def __init__(self, model):
        super(AppRegistry, self).__init__(model)

        # application type
        self.fields['app_type'] = 'addon'


class PeopleRegistry(Registry):
    """
    Registry for people applications
    """
    def __init__(self, model):
        super(PeopleRegistry, self).__init__(model)

        # application type
        self.fields['app_type'] = 'people'


class LogRegistry(Registry):
    """
    Registry for event log associated applications that are not
    classified as core, plugin or people.
    """

    def __init__(self, model):
        super(LogRegistry, self).__init__(model)

        # application type
        self.fields['app_type'] = 'log'
