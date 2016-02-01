# -*- coding: utf-8
from __future__ import unicode_literals
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.core.urlresolvers import reverse
from tendenci.apps.perms.utils import update_perms_and_save

from .models import Category, Forum, Topic, Post, Profile, Attachment, PollAnswer
from .forms import CategoryAdminForm

import compat, util
username_field = compat.get_username_field()


class ForumInlineAdmin(admin.TabularInline):
    model = Forum
    fields = ['name', 'hidden', 'position']
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'position', 'hidden', 'forum_count']
    list_per_page = 20
    ordering = ['position']
    search_fields = ['name']
    list_editable = ['position']
    fieldsets = (
        (None, {'fields': ('name', 'position', 'slug', 'status_detail')}),
        (_('Permissions'), {'fields': (('hidden',), ('allow_anonymous_view',))}),
        (_('Advanced Permissions'), {'classes': ('collapse',),'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
    )
    
    form = CategoryAdminForm

    inlines = [ForumInlineAdmin]
    
    def get_queryset(self, request):
        qs = super(CategoryAdmin, self).get_queryset(request)
        # filter out soft-deleted items
        return qs.filter(status=True)
        
    
    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)
        instance = update_perms_and_save(request, form, instance)
        instance.save()
        return instance


class ForumAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'category', 'hidden', 'position', 'topic_count', ]
    list_per_page = 20
    raw_id_fields = ['moderators']
    ordering = ['-category']
    search_fields = ['name', 'category__name']
    list_editable = ['position', 'hidden']
    fieldsets = (
        (None, {
                'fields': ('category', 'parent', 'name', 'hidden', 'position', )
                }
         ),
        (_('Additional options'), {
                'classes': ('collapse',),
                'fields': ('updated', 'description', 'headline', 'post_count', 'moderators', 'slug')
                }
            ),
        )


class PollAnswerAdmin(admin.TabularInline):
    model = PollAnswer
    fields = ['text', ]
    extra = 0


class TopicAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'forum', 'created', 'head', 'post_count', 'poll_type',]
    list_per_page = 20
    raw_id_fields = ['user', 'subscribers']
    ordering = ['-created']
    date_hierarchy = 'created'
    search_fields = ['name']
    fieldsets = (
        (None, {
                'fields': ('forum', 'name', 'user', ('created', 'updated'), 'poll_type', 'poll_question',)
                }
         ),
        (_('Additional options'), {
                'classes': ('collapse',),
                'fields': (('views', 'post_count'), ('sticky', 'closed'), 'on_moderation', 'subscribers', 'slug')
                }
         ),
        )
    inlines = [PollAnswerAdmin, ]
    
    def get_form(self, request, obj=None, **kwargs):
        form = super(TopicAdmin, self).get_form(request, obj=obj, **kwargs)
        form.base_fields['user'].initial = request.user
        form.base_fields['created'].initial = datetime.now()
        form.base_fields['updated'].initial = datetime.now()
        return form


class TopicReadTrackerAdmin(admin.ModelAdmin):
    list_display = ['topic', 'user', 'time_stamp']
    search_fields = ['user__%s' % username_field]

class ForumReadTrackerAdmin(admin.ModelAdmin):
    list_display = ['forum', 'user', 'time_stamp']
    search_fields = ['user__%s' % username_field]

class PostAdmin(admin.ModelAdmin):
    list_display = ['topic', 'user', 'created', 'updated', 'summary']
    list_per_page = 20
    raw_id_fields = ['user', 'topic']
    ordering = ['-created']
    date_hierarchy = 'created'
    search_fields = ['body']
    fieldsets = (
        (None, {
                'fields': ('topic', 'user')
                }
         ),
        (_('Additional options'), {
                'classes': ('collapse',),
                'fields' : (('created', 'updated'), 'user_ip')
                }
         ),
        (_('Message'), {
                'fields': ('body', 'body_html', 'body_text')
                }
         ),
        )


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'time_zone', 'language', 'post_count']
    list_per_page = 20
    ordering = ['-user']
    search_fields = ['user__%s' % username_field]
    fieldsets = (
        (None, {
                'fields': ('time_zone', 'language')
                }
         ),
        (_('Additional options'), {
                'classes': ('collapse',),
                'fields' : ('avatar', 'signature', 'show_signatures')
                }
         ),
        )


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['file', 'size', 'admin_view_post', 'admin_edit_post']

    def admin_view_post(self, obj):
        return '<a href="%s">view</a>' % obj.post.get_absolute_url()
    admin_view_post.allow_tags = True
    admin_view_post.short_description = _('View post')

    def admin_edit_post(self, obj):
        return '<a href="%s">edit</a>' % reverse('admin:forums_post_change', args=[obj.post.pk])
    admin_edit_post.allow_tags = True
    admin_edit_post.short_description = _('Edit post')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Attachment, AttachmentAdmin)

if util.get_pybb_profile_model() == Profile:
    admin.site.register(Profile, ProfileAdmin)

# This can be used to debug read/unread trackers

#admin.site.register(TopicReadTracker, TopicReadTrackerAdmin)
#admin.site.register(ForumReadTracker, ForumReadTrackerAdmin)