from django.template import Library
register = Library()


@register.filter
def is_directory_owner_with_membership(directory, user):
    return directory.has_membership_with(user)
