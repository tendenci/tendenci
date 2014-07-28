from django.conf import settings
from django.contrib import admin

from tendenci.core.perms.admin import TendenciBaseModelAdmin

from tendenci.apps.navs.forms import NavForm, ItemAdminForm
from tendenci.apps.navs.models import Nav, NavItem


class ItemAdmin(admin.TabularInline):
    model = NavItem
    form = ItemAdminForm
    extra = 0
    ordering = ("position",)
    template = 'admin/navs/edit_inline/tabular.html'


class NavAdmin(TendenciBaseModelAdmin):
    inlines = (ItemAdmin,)
    list_display = ("title",)

    fieldsets = (
        (None, {"fields": ("title", "description")}),
        ('Permissions', {'fields': ('status_detail', 'allow_anonymous_view',)}),
        ('Advanced Permissions', {'classes': ('collapse',), 'fields': (
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
