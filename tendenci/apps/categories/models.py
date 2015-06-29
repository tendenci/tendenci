from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Manager

from tendenci.apps.categories.utils import prep_category


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
            cat_item = None

        if cat_item:
            cat_item.delete()

    def get_for_model(self, model, category=None):
        """
        Returns a 2-tuple with lists inside. The tuple
        contains a list of categories and sub_categories.
        """
        ct = ContentType.objects.get_for_model(model)
        filters = {'content_type':ct}

        cat_items = CategoryItem.objects.filter(**filters).select_related('category__name','parent__name')
        categories = []
        sub_categories = []
        for cat in cat_items:
            if cat.category and cat.category not in categories:
                categories.append(cat.category)
            elif cat.parent and cat.parent not in sub_categories:
                sub_categories.append(cat.parent)

        #categories = set([c.category for c in cat_items if c.category])
        #sub_categories = set([self.get(pk=c.parent.pk) for c in cat_items if c.parent])

        # find all cat_items using category (ct & object_id)
        # find all cat_items using objects found within cat_items
        # find all subcategories associated with that object
        # return category from list of cat_items returned

        if category:
            filters['category'] = category

            cat_items = CategoryItem.objects.filter(**filters)

            cat_items2 = []
            for cat_item in cat_items:
                cat_items3 = CategoryItem.objects.filter(
                    content_type=cat_item.content_type,
                    object_id=cat_item.object_id,
                )
                for i in cat_items3:
                    cat_items2.append(i)

            sub_categories = set([self.get(pk=c.parent.pk) for c in cat_items2 if c.parent])

        categories = sorted(categories, key=lambda category: category.name)
        sub_categories = sorted(sub_categories, key=lambda sub_categories: sub_categories.name)

        return (categories, sub_categories)


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

    def __unicode__(self):
        return self.name
    
    class Meta:
        app_label = 'categories'

class CategoryItem(models.Model):
    content_type = models.ForeignKey(ContentType, db_index=True)
    object_id = models.PositiveIntegerField()
    category = models.ForeignKey(Category, related_name='%(class)s_category',null=True,blank=True)
    parent = models.ForeignKey(Category, related_name='%(class)s_parent', null=True,blank=True)
    object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        app_label = 'categories'

    def __unicode__(self):
        if self.category:
            return self.category.name
        return ""
