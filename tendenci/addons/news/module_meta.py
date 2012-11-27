from django.utils.html import strip_tags
from django.utils.text import unescape_entities
from tendenci.core.meta.utils import generate_meta_keywords
from tendenci.core.site_settings.utils import get_setting
from django.utils.text import truncate_words

from tendenci.core.categories.models import Category

class NewsMeta():

    def get_title(self):
        object = self.object

        ### Assign variables -----------------------  
        primary_keywords = get_setting('site','global','siteprimarykeywords')
        geo_location = get_setting('site','global','sitegeographiclocation')
        site_name = get_setting('site','global','sitedisplayname')
        category = Category.objects.get_for_object(object, 'category')
        subcategory = Category.objects.get_for_object(object, 'subcategory')

        contact_name = '%s %s' % (
            object.first_name, 
            object.last_name
        )
        contact_name = contact_name.strip()

        ### Build string -----------------------
        value = '%s - %s' % (object.headline, object.release_dt)
        value = value.strip()

        value = ''

        # start w/ headline
        if object.headline:
            value += object.headline

        # contact release
        if object.headline and object.release_dt:
            value += ' - %s' % object.release_dt.strftime('%m-%d-%Y')
        elif object.release_dt:
            value += object.release_dt.strftime('%m-%d-%Y')

        # primary keywords OR category/subcategory
        if primary_keywords:
            value = '%s : %s' % (value, primary_keywords)
        else:
            if category:
                value = '%s %s' % (value, category)
            if category and subcategory:
                value = '%s : %s' % (value, subcategory)

        value = '%s news' % value

        if contact_name:
            value = '%s contact: %s' % (value, contact_name)

        value = '%s news for %s' % (value, site_name)

        if geo_location:
            value = '%s in %s' % (value, geo_location)

        return value

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
    
    
