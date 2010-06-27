from django.db import models
from django.utils.functional import curry
from django.db.models.signals import post_init
from meta.utils import generate_meta_keywords

class Meta(models.Model):
    """
    Meta holds meta-information about an object.
    This meta information has to do with html-meta tags,
    such as: title, keyword and description.
    """
    title = models.CharField(max_length=200, blank=True)
    keywords = models.TextField(blank=True)
    description = models.TextField(blank=True)
    canonical_url = models.URLField(max_length=500, blank=True)

    update_dt = models.DateTimeField(auto_now=True)
    create_dt = models.DateTimeField(auto_now_add=True)

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
        
    def add_accessor_methods(self):
        """
        Dynamically create Meta methods.
        self.get_<type>() method
        """
        for field in ('keywords','title','description'):
            setattr(self,'get_%s' % field, curry(self.__get_meta, field))


def add_methods(sender, instance, signal, *args, **kwargs):
    """
    A listener that calls 'add_accessor_method' on
    post-init signal
    """
    if hasattr(instance, 'add_accessor_methods'):
        instance.add_accessor_methods()
# connect the add_accessor_methods function to the post_init signal
post_init.connect(add_methods, sender=Meta)
