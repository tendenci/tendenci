from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db.models import Manager, Q

from categories.utils import prep_category

class CategoryManager(Manager):
    def update(self, object, value, type):
        ct = ContentType.objects.get_for_model(object)
        object_id = object.pk     
                
        # get the category
        category = self.get_or_create(name=prep_category(value))[0]

        cat_item_filters = {
            'content_type': ct,
            'object_id': object_id
        }   
    
        # they can only be in one sub category or category
        if type == 'category':
            cat_item_filters.update({'parent__exact':None})
            cat_item = CategoryItem._default_manager.get_or_create(**cat_item_filters)[0]
            cat_item.category = category
            cat_item.save()
        else: # sub category
            cat_item_filters.update({'category__exact':None})
            cat_item = CategoryItem._default_manager.get_or_create(**cat_item_filters)[0]
            cat_item.parent = category
            cat_item.save()
             
    
    def remove(self, object, type):
        ct = ContentType.objects.get_for_model(object)
        object_id = object.pk     
 
        cat_item_filters = {
            'content_type': ct,
            'object_id': object_id
        }
                           
        if type == 'category':
            cat_item_filters.update({'parent__exact':None})
        else:
            cat_item_filters.update({'category__exact':None})  
        
        try:
            cat_item = CategoryItem._default_manager.get(**cat_item_filters)
        except:
            print 'error'
            cat_item = None
        
        print cat_item
        if cat_item:
            cat_item.delete()
          
    def get_for_object(self, object, type):
        ct = ContentType.objects.get_for_model(object)
        object_id = object.pk

        cat_item_filters = {
            'content_type': ct,
            'object_id': object_id 
        }
        
        categories = CategoryItem._default_manager.filter(**cat_item_filters)

        if not categories: return None
        
        if type == 'category':
            for cat in categories:
                if cat.category:
                    return cat.category
        else: #it's a sub category
            for cat in categories:
                if cat.parent_id > 0:
                    return self.get(pk=cat.parent_id)
        return None
        
class Category(models.Model):
    name = models.CharField(max_length=255, db_index=True, unique=True)
    
    objects = CategoryManager()

class CategoryItem(models.Model):
    content_type = models.ForeignKey(ContentType, db_index=True)
    object_id = models.PositiveIntegerField()
    category = models.ForeignKey(Category, related_name='%(class)s_category',null=True)
    parent = models.ForeignKey(Category, related_name='%(class)s_parent', null=True)
    object = generic.GenericForeignKey('content_type', 'object_id')
    
    