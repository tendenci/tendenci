__ALL__ = [
    'AlreadyRegistered',
    'NotRegistered',
    'FieldNotAllowed',
    'FieldError',
    'PackageImportError'
]


class RegistryError(Exception):
    """
    Base exception for the registry app
    """
    pass


class AlreadyRegistered(RegistryError):
    """
    Raise when model is already registered with the site
    """
    pass


class NotRegistered(RegistryError):
    """
    Raise when model is not registered with the site
    """
    pass


class FieldNotAllowed(RegistryError):
    """
    Raise when field in registry is not in allowed fields
    """
    pass


class FieldError(RegistryError):
    """
    Raise when field in registry is of the wrong type
    """
    pass


class PackageImportError(RegistryError):
    """
    Raise when the packages list in the apps registry fails to import
    """
    pass
