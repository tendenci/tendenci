from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
#
from tendenci.apps.newsletters.models import Newsletter
from tendenci.apps.perms.admin import TendenciBaseModelAdmin


def clone_selected(modeladmin, request, queryset):
    """
    Approves selected corp memberships.
    """
    for newsletter in queryset:
        newsletter.clone(request_user=request.user)

clone_selected.short_description = 'Clone selected'


class NewsletterAdmin(TendenciBaseModelAdmin):
    list_display = ['subject', 'member_only', 'group', 'date_created', 'send_status', 'date_email_sent', 'email_sent_count']
    search_fields = ['subject',]
    list_filter = [('group', admin.RelatedOnlyFieldListFilter), 'send_status']

    actions = [clone_selected,]

    def add_view(self, request, form_url='', extra_context=None):
        return HttpResponseRedirect(
                    reverse('newsletter.orig.generator')
                )

    @mark_safe
    def edit_link(self, instance):
        if instance and instance.send_status == 'draft':
            link = reverse('newsletter.action.step4', kwargs={'pk': instance.pk})
        else:
            link = reverse('newsletter.detail.view',args=[instance.id])
        return _(f'<a href="{link}">Edit</a>')
    edit_link.short_description = _('edit')


admin.site.register(Newsletter, NewsletterAdmin)
