from django.utils.html import strip_tags
from django.utils.text import unescape_entities
from meta.utils import generate_meta_keywords

class PageMeta():

    def get_title(self):
        return self.object.title

    def get_description(self):
        return_value = self.object.content
        return_value = strip_tags(return_value)
        return_value = unescape_entities(return_value)
        return_value = return_value.replace("\n","")
        return_value = return_value.replace("\r","")

        return return_value

    def get_keywords(self):
        return generate_meta_keywords(self.object.content)

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