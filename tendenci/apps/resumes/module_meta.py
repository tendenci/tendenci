from django.utils.html import strip_tags
from django.utils.text import unescape_entities
from tendenci.apps.meta.utils import generate_meta_keywords
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.base.utils import truncate_words

from tendenci.apps.categories.models import Category

class ResumeMeta():

    def get_title(self):
        object = self.object

        ### Assign variables -----------------------
        site_name = get_setting('site','global','sitedisplayname')

        ### Build string -----------------------
        value = ''

        # start w/ title
        if object.title:
            value += object.title

        # location
        if object.location:
            value = '%s - %s' % (value, object.location)

        # description
        # TODO truncate at 400 characters
        #if object.description:
        #    value = '%s - %s' % (value, object.description)

        value = '%s - employment opportunity or resume position %s' % (value, site_name)

        return value

    def get_description(self):
        object = self.object

        ### Assign variables -----------------------
        site_name = get_setting('site','global','sitedisplayname')

        ### Build string -----------------------
        value = ''

        # start w/ title
        if object.title:
            value += object.title

        # location
        if object.location:
            value = '%s - %s' % (value, object.location)

        # description
        # TODO truncate at 450 characters
        if object.description:
            value = '%s - %s' % (value, object.description)

        value = '%s - employment opportunity %s' % (value, site_name)

        return value

    def get_keywords(self):
        object = self.object

        ### Assign variables -----------------------
        dynamic_keywords = generate_meta_keywords(object.description)
        site_name = get_setting('site','global','sitedisplayname')
        site_name = site_name.strip()

        #T4 used title, experience, skills, education and description

        list = [
            site_name,
            'employment opportunity',
            'resumes',
        ]

        # remove blank items
        for item in list:
            if not item.strip():
                list.remove(item)
            value = '%s, %s' % (', '.join(list), dynamic_keywords)

        return value

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
