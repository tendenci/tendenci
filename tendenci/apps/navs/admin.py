from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ngettext
from django.contrib import messages

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.theme.templatetags.static import static
from tendenci.apps.navs.forms import NavForm, ItemAdminForm
from tendenci.apps.navs.models import Nav, NavItem


class ItemAdmin(admin.TabularInline):
    model = NavItem
    form = ItemAdminForm
    extra = 0
    ordering = ("position",)
    template = 'admin/navs/edit_inline/tabular.html'

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(ItemAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'page':
            formfield.choices = formfield.choices
        return formfield


class NavAdmin(TendenciBaseModelAdmin):
    inlines = (ItemAdmin,)
    list_display = ("title", "status_detail")

    fieldsets = (
        (None, {"fields": ("title", "description")}),
        (_('Permissions'), {'fields': ('status_detail', 'allow_anonymous_view',)}),
        (_('Advanced Permissions'), {'classes': ('collapse',), 'fields': (
            'user_perms',
            'group_perms',
        )}),
    )

    form = NavForm
    actions = ['inactivate_selected']

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js',
            static('js/admin/form-fields-inline-ordering.js'),
            static('js/admin/navitem-inline.js'),
        )
        css = {'all': [static('css/admin/dynamic-inlines-with-sort.css'),
                       static('css/admin/navitem-inline.css'),
                       static('css/admin/navchangelist.css')], }

    def inactivate_selected(self, request, queryset):
        """
        Inactivate the selected navs.
        """
        updated = queryset.update(status_detail='inactive')
        self.message_user(request, ngettext(
                '%d nav was successfully marked as Inactive.',
                '%d navs were successfully marked as Inactive.',
                updated,
            ) % updated, messages.SUCCESS)
    
    inactivate_selected.short_description = 'Mark selected navs as Inactive'

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        if 'soft_delete_selected' in actions:
            del actions['soft_delete_selected']
        return actions


admin.site.register(Nav, NavAdmin)
