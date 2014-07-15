from django.utils.html import strip_tags
from django.utils.text import unescape_entities
from tendenci.core.meta.utils import generate_meta_keywords
from tendenci.core.site_settings.utils import get_setting
from django.utils.text import truncate_words
from django.utils.html import strip_tags, strip_entities

from tendenci.core.categories.models import Category

class EventMeta():
    """
    SEO specific tags carefully constructed follow.  These must *NOT* be perfect
    but rather should be strong. - ES

    create a search engine friendly html TITLE tag for the page
    - we want similar phrases but NOT the exact same between TITLE and META tags
    - It MUST produce the exact same result if the spider returns but must also differ
    by site for sites that feed from the same central data
    """
    def get_title(self):
        # TODO: Optimize this SEM algorithm
        return self.object.title

    def get_description(self):
        # TODO: Optimize this SEM algorithm
        description = self.object.description

        description = strip_tags(description)
        description = strip_entities(description)
        description = truncate_words(description, 40, '')
        return description

    def get_keywords(self):
        # TODO: Optimize this SEM algorithm
        return generate_meta_keywords(self.object.description)

    def get_canonical_url(self):
        object = self.object
        return object.get_absolute_url()

    def get_meta(self, object, name):

        self.object = object
        self.name = name

        if name == 'title':
            if object.meta and object.meta.title: return object.meta.title
            else: return self.get_title()
        elif name == 'description':
            if object.meta and object.meta.description: return object.meta.description
            else: return self.get_description()
        elif name =='keywords':
            if object.meta and object.meta.keywords: return object.meta.keywords
            else: return self.get_keywords()
        elif name =='canonical_url':
            if object.meta and object.meta.canonical_url: return object.meta.canonical_url
            else: return self.get_canonical_url()
        return ''


