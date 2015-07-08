from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from tendenci.core.perms.admin import TendenciBaseModelAdmin

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
    list_display = ("title",)

    fieldsets = (
        (None, {"fields": ("title", "description")}),
        (_('Permissions'), {'fields': ('status_detail', 'allow_anonymous_view',)}),
        (_('Advanced Permissions'), {'classes': ('collapse',), 'fields': (
            'user_perms',
            'group_perms',
        )}),
    )

    form = NavForm

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.11.0/jquery-ui.min.js',
            '%sjs/admin/form-fields-inline-ordering.js' % settings.STATIC_URL,
            '%sjs/admin/navitem-inline.js' % settings.STATIC_URL,
        )
        css = {'all': ['%scss/admin/dynamic-inlines-with-sort.css' % settings.STATIC_URL,
                       '%scss/admin/navitem-inline.css' % settings.STATIC_URL,
                       '%scss/admin/navchangelist.css' % settings.STATIC_URL], }

admin.site.register(Nav, NavAdmin)
