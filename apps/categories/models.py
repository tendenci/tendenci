from django.db import models
#from django.contrib.contenttypes import generic
#from django.contrib.contenttypes.models import ContentType
#from django.utils.translation import ugettext_lazy as _

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    parent = models.ForeignKey('self', blank=True, null=True, related_name='child')
    description = models.TextField(blank=True,help_text="Optional")
    
    class Admin:
        list_display = ('name', '_parents_repr')
    
    def __str__(self):
        p_list = self._recurse_for_parents(self)
        p_list.append(self.name)
        return self.get_separator().join(p_list)
    
    def get_absolute_url(self):
        if self.parent_id:
            return "/tag/%s/%s/" % (self.parent.slug, self.slug)
        else:
            return "/tag/%s/" % (self.slug)
    
    def _recurse_for_parents(self, cat_obj):
        p_list = []
        if cat_obj.parent_id:
            p = cat_obj.parent
            p_list.append(p.name)
            more = self._recurse_for_parents(p)
            p_list.extend(more)
        if cat_obj == self and p_list:
            p_list.reverse()
        return p_list
        
    def get_separator(self):
        return ' :: '
    
    def _parents_repr(self):
        p_list = self._recurse_for_parents(self)
        return self.get_separator().join(p_list)
    _parents_repr.short_description = "Tag parents"
    
    def save(self):
        p_list = self._recurse_for_parents(self)
        if self.name in p_list:
#            raise validators.ValidationError("You must not save a category in itself!")
            print 'broken'
        super(Category, self).save()

#class Category(models.Model):
#    """
#    A category.
#    """
#    name = models.CharField(_('name'), max_length=50, unique=True, db_index=True)
#
#    def __unicode__(self):
#        return self.name
#
#class CategoryItem(models.Model):
#    """
#    Holds the relationship between a category and the item being categorized.
#    """
#    category = models.ForeignKey(Category, related_name='items')
#    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'))
#    object_id = models.PositiveIntegerField(_('object id'), db_index=True)
#    object = generic.GenericForeignKey('content_type', 'object_id')
#
#    class Meta:
#        # Enforce unique tag association per object
#        unique_together = (('category', 'content_type', 'object_id'),)
#        verbose_name = _('categorized item')
#        verbose_name_plural = _('categorized items')
#
#    def __unicode__(self):
#        return u'%s [%s]' % (self.object, self.category)