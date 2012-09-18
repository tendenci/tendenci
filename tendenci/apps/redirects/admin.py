from django.contrib import admin

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.redirects.models import Redirect
from tendenci.apps.redirects.forms import RedirectForm

class RedirectAdmin(TendenciBaseModelAdmin):
    list_display = [ ]#'title', 'post_dt', 'owner_link', 'admin_perms', 'admin_status']
    list_filter = [] #'status_detail', 'owner_username']
    prepopulated_fields = {}#'slug': ['title']}
#    search_fields = ['title', 'description']
#    fieldsets = (
#        ('Redirect Information', {
#            'fields': ('title',
#                       'slug',
#                       'description',
#                       'skills',
#                       'location',
#                       'contact_email',
#                       'contact_website',
#                       'tags',
#                       'post_dt',
#                )
#        }),
#        ('Permissions', {'fields': ('allow_anonymous_view',)}),
#        ('Advanced Permissions', {'classes': ('collapse',), 'fields': (
#            'user_perms',
#            'member_perms',
#            'group_perms',
#            )}),
#        ('Status', {'fields': (
#            'status',
#            'status_detail',
#            )}),
#        )
    form = RedirectForm
    ordering = ['-update_dt']

admin.site.register(Redirect, RedirectAdmin)