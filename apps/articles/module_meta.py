from django.utils.html import strip_tags
from django.utils.text import unescape_entities
from meta.utils import generate_meta_keywords
from site_settings.utils import get_setting
from django.utils.text import truncate_words

from categories.models import Category

class ArticleMeta():
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
        category = Category.objects.get_for_object(object, 'category')
        subcategory = Category.objects.get_for_object(object, 'subcategory')

        creator_name = '%s %s' % (
            object.creator.first_name, 
            object.creator.last_name
        )
        creator_name = creator_name.strip()

        ### Build string -----------------------
        value = '%s - %s' % (object.headline, object.release_dt)

        if primary_keywords:
            value = '%s : %s' % (value, primary_keywords)
        else:
            if category:
                value = '%s %s' % (value, category)
            if category and subcategory:
                value = '%s : %s' % (value, subcategory)

        value = '%s article' % value

        if creator_name:
            value = '%s contact: %s' % (value, creator_name)

        value = '%s articles for %s' % (value, site_name)

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
        creator_name = '%s %s' % (
            object.creator.first_name, 
            object.creator.last_name
        )
        creator_name = creator_name.strip()

        if object.summary:
            content = object.summary
        elif object.body:
            content = object.body

        content = strip_tags(content)
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

            value = '%s article' % value

        value = '%s Articles and White Papers for %s %s' % (
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

        creator_name = '%s %s' % (
            object.creator.first_name, 
            object.creator.last_name
        )

        ### Build string -----------------------
        value = ''

        if primary_keywords:
            value = '%s %s' % (value, primary_keywords)

        if object.headline:
            list = [
                'Articles',
                geo_location,
                site_name,
                'white paper',
                creator_name,
            ]
            value = '%s %s %s' % (value, ''.join(list), dynamic_keywords)

        else:
            list = [
                'Articles',
                geo_location,
                site_name,
                'white paper',
                secondary_keywords,
            ]
            value = '%s %s' % (value, ''.join(list))
        


        return generate_meta_keywords(self.object.body)

    def get_meta(self, object, name):

        self.object = object
        self.name = name
        
        if self.name == 'title':
            return self.get_title()
        elif self.name == 'description':
            return self.get_description()
        elif self.name =='keywords':
            return self.get_keywords()

        return ''
    


