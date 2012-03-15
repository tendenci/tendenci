from django.contrib import admin
from django.core.urlresolvers import reverse
from django.conf import settings

from notification.models import (NoticeType, NoticeSetting, Notice,
    ObservedItem, NoticeEmail)
    
class NoticeTypeAdmin(admin.ModelAdmin):
    list_display = ('label', 'display', 'description', 'default')

class NoticeSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'notice_type', 'medium', 'send')

class NoticeAdmin(admin.ModelAdmin):
    list_display = ('message', 'user', 'notice_type', 'added', 'unseen', 'archived')

class NoticeEmailAdmin(admin.ModelAdmin):
    list_display = ('title', 'emails', 'view_on_site')
    actions = ['resend']
    
    def view_on_site(self, obj):
        link_icon = '%simages/icons/external_16x16.png' % settings.STATIC_URL
        link = '<a href="%s" title="%s"><img src="%s" /></a>' % (
            reverse('notification_email', args=[obj.guid]),
            obj,
            link_icon,
        )
        return link
    view_on_site.allow_tags = True
    view_on_site.short_description = 'view'
    
    def resend(self, request, queryset):
        for q in queryset:
            q.resend()
    resend.short_description = "Resend the selected emails"

admin.site.register(NoticeType, NoticeTypeAdmin)
admin.site.register(NoticeSetting, NoticeSettingAdmin)
admin.site.register(Notice, NoticeAdmin)
admin.site.register(ObservedItem)
admin.site.register(NoticeEmail, NoticeEmailAdmin)
