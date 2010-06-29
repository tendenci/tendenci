from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

# Django admin
from django.contrib import admin
admin.autodiscover()

# authority permissions
import authority
authority.autodiscover()

urlpatterns = patterns('',
    url(r'^$', direct_to_template, {"template": "homepage.html",}, name="home"),
    (r'^admin/', include(admin.site.urls)),
    (r'^base/', include('base.urls')),
    (r'^avatar/', include('avatar.urls')),
    (r'^dashboard/', include('dashboard.urls')),
    (r'^categories/', include('categories.urls')),
    (r'^articles/', include('articles.urls')),
    (r'^entities/', include('entities.urls')),
    (r'^locations/', include('locations.urls')),
    (r'^pages/', include('pages.urls')),
    (r'^users/', include('profiles.urls')),
    (r'^photos/', include('photos.urls')),
    (r'^profiles/', include('profiles.urls')),
    (r'^groups/', include('user_groups.urls')),
    (r'^stories/', include('stories.urls')),
    (r'^invoices/', include('invoices.urls')),
    (r'^py/', include('make_payments.urls')),
    (r'^payments/', include('payments.urls')),
    (r'^accountings/', include('accountings.urls')),
    (r'^emails/', include('emails.urls')),
    (r'^news/', include('news.urls')),
    (r'^settings/', include('site_settings.urls')),
    (r'^files/', include('files.urls')),
    (r'^contacts/', include('contacts.urls')),
    (r'^accounts/', include('accounts.urls')),
    (r'^search/', include('search.urls')),
    (r'^event-logs/', include('event_logs.urls')),
    (r'^contributions/', include('contributions.urls')),
    (r'^theme-editor/', include('theme_editor.urls')),
    (r'^jobs/', include('jobs.urls')),
    (r'^contact/', include('form_builder.urls')),
    (r'^sitemap.xml', include('sitemaps.urls')),
    # third party (inside environment)
    (r'^tinymce/', include('tinymce.urls')),
    (r'^captcha/', include('captcha.urls')),
)

handler500 = 'base.views.custom_error'

# Local url patterns for development
try:
    from local_urls import MEDIA_PATTERNS
    urlpatterns += MEDIA_PATTERNS
except ImportError:
    pass