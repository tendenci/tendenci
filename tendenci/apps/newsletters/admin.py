from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from tendenci.apps.newsletters.models import NewsletterTemplate, Newsletter
from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.theme.templatetags.static import static


class NewsletterTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'rendered_view', 'content_view']

    @mark_safe
    def rendered_view(self, obj):
        link_icon = static('images/icons/external_16x16.png')
        link = '<a href="%s" title="%s"><img src="%s" alt="External 16x16" title="external 16x16" /></a>' % (
            obj.get_absolute_url(),
            obj,
            link_icon,
        )
        return link
    rendered_view.short_description = _('view rendered template')

    @mark_safe
    def content_view(self, obj):
        link_icon = static('images/icons/external_16x16.png')
        link = '<a href="%s" title="%s"><img src="%s" alt="External 16x16" title="external 16x16" /></a>' % (
            obj.get_content_url(),
            obj,
            link_icon,
        )
        return link
    content_view.short_description = _('view template content')


class NewsletterAdmin(TendenciBaseModelAdmin):
    pass

admin.site.register(NewsletterTemplate, NewsletterTemplateAdmin)

admin.site.register(Newsletter, NewsletterAdmin)
