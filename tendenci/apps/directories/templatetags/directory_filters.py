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
