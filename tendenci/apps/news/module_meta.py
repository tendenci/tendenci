from django.utils.html import strip_tags
from django.utils.text import unescape_entities
from tendenci.apps.meta.utils import generate_meta_keywords
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.base.utils import truncate_words

from tendenci.apps.categories.models import Category

class NewsMeta():

    def get_title(self):
        obj = self.object

        ### Assign variables -----------------------
        primary_keywords = get_setting('site','global','siteprimarykeywords')
        geo_location = get_setting('site','global','sitegeographiclocation')
        site_name = get_setting('site','global','sitedisplayname')
        category = Category.objects.get_for_object(obj, 'category')
        subcategory = Category.objects.get_for_object(obj, 'subcategory')

        contact_name = '%s %s' % (
            obj.first_name,
            obj.last_name
        )
        contact_name = contact_name.strip()

        ### Build string -----------------------
        values_list = []
        if obj.headline:
            values_list.append(obj.headline)

        if obj.headline and obj.release_dt:
            values_list.append('-')
        if obj.release_dt:
            values_list.append(obj.release_dt.strftime('%m-%d-%Y'))

        if primary_keywords:
            if values_list:
                values_list.append(':')
                values_list.append(primary_keywords)
        else:
            if category and subcategory:
                values_list.append('category')
                values_list.append(':')
                values_list.append('subcategory')
            elif category:
                values_list.append('category')

        if site_name:
            if values_list:
                values_list.append('news for')
            values_list.append(site_name)

        if contact_name:
            values_list.append('contact: %s' % contact_name)

        if geo_location:
            values_list.append('in %s' % geo_location)

        title = ' '.join(values_list)

        return title

    def get_description(self):
        object = self.object

        ### Assign variables -----------------------
        primary_keywords = get_setting('site','global','siteprimarykeywords')
        category = Category.objects.get_for_object(object, 'category')
        subcategory = Category.objects.get_for_object(object, 'subcategory')
        site_name = get_setting('site','global','sitedisplayname')
        geo_location = get_setting('site','global','sitegeographiclocation')
        contact_name = '%s %s' % (
            object.first_name,
            object.last_name
        )
        contact_name = contact_name.strip()

        if object.summary:
            content = object.summary
        else:
            content = object.body

        content = strip_tags(content) #strips HTML tags
        content = unescape_entities(content)
        content = content.replace("\n","").replace("\r","")
        content = truncate_words(content, 50) # ~ about 250 chars

        ### Build string -----------------------
        value = object.headline

        if contact_name:
            value = '%s %s' % (value, contact_name)

        value = '%s : %s' % (value, content)

        if primary_keywords:
            value = '%s %s' % (value, primary_keywords)
        else:
            if category:
                value = '%s %s' % (value, category)
            if category and subcategory:
                value = '%s : %s' % (value, subcategory)

            value = '%s news' % value

        value = '%s News and Press Releases for %s %s' % (
            value, site_name, geo_location)

        value = value.strip()

        return value

    def get_keywords(self):
        object = self.object

        ### Assign variables -----------------------
        dynamic_keywords = generate_meta_keywords(object.body)
        primary_keywords = get_setting('site','global','siteprimarykeywords')
        secondary_keywords = get_setting('site','global','sitesecondarykeywords')
        geo_location = get_setting('site','global','sitegeographiclocation')
        site_name = get_setting('site','global','sitedisplayname')

        contact_name = '%s %s' % (
            object.first_name,
            object.last_name
        )

        ### Build string -----------------------
        value = ''

        if primary_keywords:
            value = '%s %s' % (value, primary_keywords)
            value = value.strip()

        if object.headline:
            list = [
                'News',
                geo_location,
                site_name,
                'white paper',
                contact_name,
            ]

            # remove blank items
            for item in list:
                if not item.strip():
                    list.remove(item)

            value = '%s %s, %s' % (value, ', '.join(list), dynamic_keywords)

        else:
            list = [
                'News',
                geo_location,
                site_name,
                'white paper',
                secondary_keywords,
            ]
            value = '%s %s' % (value, ''.join(list))

        return value

    def get_canonical_url(self):
        return '{0}{1}'.format(get_setting('site', 'global', 'siteurl'), self.object.get_absolute_url())

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
