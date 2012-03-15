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
    list_display = ('preview_email', 'date_sent')
    actions = ['resend']

    def preview_email(self, obj):
        return '<a href="%s">%s</a>' % \
            (reverse('notification_email', args=[obj.guid]), obj.title)
    preview_email.allow_tags = True
    preview_email.short_description = 'Preview Email'

    def resend(self, request, queryset):
        for q in queryset:
            print q.resend()
    resend.short_description = "Resend the selected emails"

admin.site.register(NoticeType, NoticeTypeAdmin)
admin.site.register(NoticeSetting, NoticeSettingAdmin)
admin.site.register(Notice, NoticeAdmin)
admin.site.register(ObservedItem)
admin.site.register(NoticeEmail, NoticeEmailAdmin)
