import copy
from registry.exceptions import AlreadyRegistered, NotRegistered
from utils import RegisteredApps


class RegistrySite(object):
    """
    Encapsulates all the registries that should be available.
    This follows the django.contrib.admim model
    """
    def __init__(self):
        self._registry = {}

    def register(self, model, registry_class=None):
        """
        Registers a model with the site.

        The model should be a Model class, not instances.

        If no registry_class is provided CoreRegistry will be applied
        to the model.
        """
        if not registry_class:
            from registry.base import CoreRegistry
            registry_class = CoreRegistry

        if not hasattr(model, '_meta'):
            raise AttributeError('The model being registered must derive from Model.')

        if model in self._registry:
            raise AlreadyRegistered('The model %s is already registered' % model.__class__)

        self._registry[model] = registry_class(model)

    def unregister(self, model):
        """
        Unregisters a model from the site.
        """
        if model not in self._registry:
            raise NotRegistered('The model %s is not registered' % model.__class__)
        del(self._registry[model])

    def get_registered_apps(self):
        return RegisteredApps(self._registry)

site = RegistrySite()
