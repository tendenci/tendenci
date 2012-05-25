from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.utils.encoding import iri_to_uri
from django.conf import settings

from event_logs.models import EventLog
from perms.utils import update_perms_and_save
from products.models import Product, ProductFile, Category, Subcategory
from products.forms import ProductForm

class ProductFileAdmin(admin.StackedInline):
    model = ProductFile
    fieldsets = (
        (None, {
            'fields': (
            'file',
            'photo_description',
            'position',
        )},),
    )
    extra = 1

class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]

class ProductAdmin(admin.ModelAdmin):
    list_display = ['view_on_site', 'edit_link', 'name', 'slug','item_number', 'tags']
    list_filter = ['category', 'subcategory']
    search_fields = ['name', 'description', 'category__name', 'subcategory__name']
    inlines = [ProductFileAdmin,]
    fieldsets = (
        (None, 
            {'fields': (
                'name',
                'slug',
                'brand',
                'url',
                'item_number',
                'category',
                'subcategory',
                'summary',
                'description',
                'tags',
            )}
        ),
        ('Permissions', {'fields': ('allow_anonymous_view',)}),
        ('Advanced Permissions', {'classes': ('collapse',),'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        ('Publishing Status', {'fields': (
            'status',
            'status_detail'
        )}),
    )
    prepopulated_fields = {'slug': ['name']}
    form = ProductForm
    actions = []
    
    class Media:
        js = (
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )

    def edit_link(self, obj):
        link = '<a href="%s" title="edit">Edit</a>' % reverse('admin:products_product_change', args=[obj.pk])
        return link
    edit_link.allow_tags = True
    edit_link.short_description = 'edit'

    def view_on_site(self, obj):
        link_icon = '%simages/icons/external_16x16.png' % settings.STATIC_URL
        link = '<a href="%s" title="%s"><img src="%s" /></a>' % (
            reverse('products.detail', args=[obj.slug]),
            obj,
            link_icon,
        )
        return link
    view_on_site.allow_tags = True
    view_on_site.short_description = 'view'

    def log_deletion(self, request, object, object_repr):
        super(ProductAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 370300,
            'event_data': '%s (%d) deleted by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)           

    def log_change(self, request, object, message):
        super(ProductAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 370200,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)               

    def log_addition(self, request, object):
        super(ProductAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 370100,
            'event_data': '%s (%d) added by %s' % (object._meta.object_name, 
                                                   object.pk, request.user),
            'description': '%s added' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)
                     
    def get_form(self, request, obj=None, **kwargs):
        """
        inject the user in the form.
        """
        form = super(ProductAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def save_model(self, request, object, form, change):
        """
        update the permissions backend
        """
        instance = form.save(commit=False)
        perms = update_perms_and_save(request, form, instance)
        return instance

    def save_formset(self, request, form, formset, change):
        for f in formset.forms:
            file = f.save(commit=False)
            if file.file:
                file.product = form.save()
                file.content_type = ContentType.objects.get_for_model(file.product)
                file.object_id = file.product.pk
                file.name = file.file.name
                file.creator = request.user
                file.owner = request.user
                file.save()
        
        formset.save()

    def change_view(self, request, object_id, extra_context=None):
        result = super(ProductAdmin, self).change_view(request, object_id, extra_context)

        if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue') and request.GET.has_key('next'):
            result['Location'] = iri_to_uri("%s") % request.GET.get('next')
        return result

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Subcategory, SubcategoryAdmin)
