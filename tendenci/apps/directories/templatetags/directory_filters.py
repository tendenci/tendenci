from django.template import Library
register = Library()


@register.filter
def is_directory_owner_with_membership(directory, user):
    return directory.has_membership_with(user)


@register.filter
def allow_request_to_associate(directory, user):
    """
    Check if this user is allowed to  submit affiliate requests to this directory.
    """
    return directory.allow_associate_by(user)

@register.filter
def from_membership(directory):
    """
    Check if this directory is created from an individual membership.
    """
    return directory.get_membership() is not None


@register.filter
def is_owner(directory, user):
    """
    Check if this user is the owner of the directory.
    """
    return directory.is_owner(user)

