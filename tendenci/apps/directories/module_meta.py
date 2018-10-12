from django.utils.html import strip_tags
from django.utils.text import unescape_entities
from tendenci.apps.meta.utils import generate_meta_keywords
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.base.utils import truncate_words

class DirectoryMeta():
    """
    SEO specific tags carefully constructed follow.  These must *NOT* be perfect
    but rather should be strong. - ES

    create a search engine friendly html TITLE tag for the page
    - we want similar phrases but NOT the exact same between TITLE and META tags
    - It MUST produce the exact same result if the spider returns but must also differ
    by site for sites that feed from the same central data
    """
    def get_title(self):
        object = self.object

        ### Assign variables -----------------------
        primary_keywords = get_setting('site','global','siteprimarykeywords')
        geo_location = get_setting('site','global','sitegeographiclocation')
        site_name = get_setting('site','global','sitedisplayname')
        category_set = object.category_set
        category = category_set.get('category', '')
        subcategory = category_set.get('sub_category', '')

        creator_name = ''
        if object.creator:
            creator_name = '%s %s' % (
                object.creator.first_name,
                object.creator.last_name
            )
        creator_name = creator_name.strip()

        ### Build string -----------------------
        value = '%s - %s' % (object.headline, object.activation_dt)
        value = value.strip()

        value = ''

        # start w/ headline
        if object.headline:
            value += object.headline

        # contact activation
        if object.headline and object.activation_dt:
            value += ' - %s' % object.activation_dt.strftime('%m-%d-%Y')
        elif object.activation_dt:
            value += object.activation_dt.strftime('%m-%d-%Y')

        # primary keywords OR category/subcategory
        if primary_keywords:
            value = '%s : %s' % (value, primary_keywords)
        else:
            if category:
                value = '%s %s' % (value, category)
            if category and subcategory:
                value = '%s : %s' % (value, subcategory)

        value = '%s directory' % value

        if creator_name:
            value = '%s contact: %s' % (value, creator_name)

        value = '%s directories for %s' % (value, site_name)

        if geo_location:
            value = '%s in %s' % (value, geo_location)

        return value

    def get_description(self):
        object = self.object

        ### Assign variables -----------------------
        primary_keywords = get_setting('site','global','siteprimarykeywords')
        category_set = object.category_set
        category = category_set.get('category', '')
        subcategory = category_set.get('sub_category', '')
        site_name = get_setting('site','global','sitedisplayname')
        geo_location = get_setting('site','global','sitegeographiclocation')
        creator_name = ''
        if object.creator:
            creator_name = '%s %s' % (
                object.creator.first_name,
                object.creator.last_name
            )
        creator_name = creator_name.strip()

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

        if creator_name:
            value = '%s %s' % (value, creator_name)

        value = '%s : %s' % (value, content)

        if primary_keywords:
            value = '%s %s' % (value, primary_keywords)
        else:
            if category:
                value = '%s %s' % (value, category)
            if category and subcategory:
                value = '%s : %s' % (value, subcategory)

            value = '%s directory' % value

        value = '%s Directories for %s %s' % (
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

        creator_name = ''
        if object.creator:
            creator_name = '%s %s' % (
                object.creator.first_name,
                object.creator.last_name
            )

        ### Build string -----------------------
        value = ''

        if primary_keywords:
            value = '%s %s' % (value, primary_keywords)
            value = value.strip()

        if object.headline:
            list = [
                'Directories',
                geo_location,
                site_name,
                'white paper',
                creator_name,
            ]

            # remove blank items
            for item in list:
                if not item.strip():
                    list.remove(item)

            value = '%s %s, %s' % (value, ', '.join(list), dynamic_keywords)

        else:
            list = [
                'Directories',
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
