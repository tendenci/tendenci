from django.contrib import admin
from django.template.defaultfilters import striptags, truncatewords
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.email_blocks.models import EmailBlock
from tendenci.apps.email_blocks.forms import EmailBlockForm


class EmailBlockAdmin(TendenciBaseModelAdmin):
    list_display = ['edit_link', 'email', 'email_domain', 'reason_truncated', 'status_detail']
    list_filter = ['email', 'email_domain', 'status_detail']
    search_fields = ['email', 'email_domain']
    fieldsets = (
        (_('Specify an email OR a domain you wish to block:'), {
            'fields': ('email',
                'email_domain',
                'reason',
                'status_detail',)
            }),
    )
    view_on_site = False
    form = EmailBlockForm
    ordering = ['-update_dt']

    @mark_safe
    def reason_truncated(self, obj):
        return truncatewords(striptags(obj.reason), 15)
    reason_truncated.short_description = _('Reason')

admin.site.register(EmailBlock, EmailBlockAdmin)
