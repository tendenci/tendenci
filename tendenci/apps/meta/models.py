from django.db import models
from django.utils.functional import curry
from django.db.models.signals import post_init
from tendenci.apps.meta.utils import generate_meta_keywords

class Meta(models.Model):
    """
    Meta holds meta-information about an object.
    This meta information has to do with html-meta tags,
    such as: title, keyword and description.
    """
    title = models.CharField(max_length=200, blank=True)
    keywords = models.TextField(blank=True)
    description = models.TextField(blank=True)
    canonical_url = models.CharField(max_length=500, blank=True)

    update_dt = models.DateTimeField(auto_now=True)
    create_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'meta'

    def generate_keywords(self, value):
        return generate_meta_keywords(value)

    def __get_meta(self, meta_name):
        """
        Used privately to create methods
        These methods call standard methods
        in related objects.
        These created methods check the database for
        meta-information first, else it dynamically
        generates that meta information.
        """
        # if meta_attr populated; return data
        # else call related object method (dynamic data)
        meta_attribute = getattr(self, meta_name)
        if meta_attribute: return meta_attribute

        # check if attribute exists; else raise exception
        if not hasattr(self.object, 'get_meta'):
            raise AttributeError, 'Method get_meta() does not exist in %s' % self.object._meta.object_name

        return getattr(self.object,'get_meta')(meta_name)

    def get_title(self):
        return self.__get_meta(self.title)
    
    def get_keywords(self):
        return self.__get_meta(self.keywords)
    
    def get_description(self):
        return self.__get_meta(self.description)
    
    def get_canonical_url(self):
        return self.__get_meta(self.canonical_url)

    def add_accessor_methods(self):
        """
        Dynamically create Meta methods.
        self.get_<type>() method
        """
        for field in ('keywords','title','description', 'canonical_url'):
            setattr(self,'get_%s' % field, curry(self.__get_meta, field))





