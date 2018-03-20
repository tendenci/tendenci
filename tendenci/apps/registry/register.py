import copy
from django.conf import settings
from importlib import import_module
from django.utils.module_loading import module_has_submodule

from tendenci.apps.registry.sites import site


def autodiscover():
    """
    Auto-discover INSTALLED_APPS app_registry.py modules and fail silently when
    not present. This forces an import on them to register any admin bits they
    may want.
    """

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        # Attempt to import the app's admin module.
        try:
            before_import_registry = copy.copy(site._registry)
            import_module('%s.app_registry' % app)
        except:
            # Reset the model registry to the state before the last import as
            # this import will have to reoccur on the next request and this
            # could raise NotRegistered and AlreadyRegistered exceptions
            # (see #8245).
            site._registry = before_import_registry

            # Decide whether to bubble up this error. If the app just
            # doesn't have an admin module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            try:
                if module_has_submodule(mod, 'app_registry'):
                    raise
            # Work-around for bug in Django <2.0 on Python >=3.4
            # https://code.djangoproject.com/ticket/28241
            except (ImportError, AttributeError):
                pass
