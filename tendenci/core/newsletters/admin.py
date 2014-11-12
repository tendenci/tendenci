from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from tendenci.core.newsletters.models import NewsletterTemplate, Newsletter


class NewsletterTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'rendered_view', 'content_view']

    def rendered_view(self, obj):
        link_icon = '%simages/icons/external_16x16.png' % settings.STATIC_URL
        link = '<a href="%s" title="%s"><img src="%s" alt="External 16x16" title="external 16x16" /></a>' % (
            obj.get_absolute_url(),
            obj,
            link_icon,
        )
        return link
    rendered_view.allow_tags = True
    rendered_view.short_description = _('view rendered template')

    def content_view(self, obj):
        link_icon = '%simages/icons/external_16x16.png' % settings.STATIC_URL
        link = '<a href="%s" title="%s"><img src="%s" alt="External 16x16" title="external 16x16" /></a>' % (
            obj.get_content_url(),
            obj,
            link_icon,
        )
        return link
    content_view.allow_tags = True
    content_view.short_description = _('view template content')


admin.site.register(NewsletterTemplate, NewsletterTemplateAdmin)

admin.site.register(Newsletter)
