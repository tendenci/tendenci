from django.utils.html import strip_tags
from django.utils.text import unescape_entities
from meta.utils import generate_meta_keywords

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
        return self.object.headline

    def get_description(self):
        if self.object.summary:
            return_value = self.object.summary
        elif self.object.body:
            return_value = self.object.body

        return_value = strip_tags(return_value)
        return_value = unescape_entities(return_value)
        return_value = return_value.replace("\n","")
        return_value = return_value.replace("\r","")

        return return_value

    def get_keywords(self):
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
    


