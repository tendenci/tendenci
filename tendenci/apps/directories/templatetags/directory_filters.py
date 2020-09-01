from django.template import Library
register = Library()


@register.filter
def directory_can_publish_by(directory, user):
    return directory.can_publish_by(user)
