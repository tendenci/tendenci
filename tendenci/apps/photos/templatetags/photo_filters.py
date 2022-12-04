from django.template import Library


register = Library()

@register.filter
def get_images(photo_set, user):
    from tendenci.apps.photos.models import PhotoSet
    if not isinstance(photo_set, PhotoSet):
        return None
    return photo_set.get_images(user=user)
