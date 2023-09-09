from django.db.models import ForeignKey, TextField
from django.core.cache import cache
from django.template import Library

from bs4 import BeautifulSoup
from tendenci.libs.tinymce.models import HTMLField

from tendenci.apps.files.models import File
from tendenci.apps.site_settings.utils import get_setting


register = Library()


@register.inclusion_tag("meta/og_image.html")
def meta_og_image(obj, field_name):
    base_url = get_setting('site', 'global', 'siteurl')
    keys = ["meta_og_image", obj._meta.app_label, str(obj.id),
            field_name, obj.update_dt.strftime('%m%d%Y%H%M%S')]
    cache_key = "_".join(keys)
    cached_value = cache.get(cache_key)
    if cached_value:
        return cached_value

    try:
        field = obj._meta.get_field(field_name)
        image_list = []

        if isinstance(field, HTMLField) or isinstance(field, TextField):
            content = getattr(obj, field_name)
            soup = BeautifulSoup(content)
            for image in soup.find_all("img"):
                image_url = image["src"]
                if image_url:
                    if image_url[0] == '/' and image_url[:2] != '//':
                        image_url = base_url + image_url
                    image_list.append(image_url)

        elif isinstance(field, ForeignKey):
            image = getattr(obj, field_name)
            if isinstance(image, File):
                image_list.append(base_url + image.get_absolute_url())

        value = {'urls': image_list}
        cache.set(cache_key, value)
        return value
    except Exception:
        return {}
