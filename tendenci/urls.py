from os.path import join
from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template, redirect_to
from django.contrib import admin
from tendenci.libs.model_report import report

from tendenci.core.registry import autodiscover as reg_autodiscover

# load the apps that are in Django Admin
admin.autodiscover()

# load the app_registry
reg_autodiscover()

# django model report
report.autodiscover()

# Admin Patterns
urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)

#report patterns
urlpatterns += patterns('',
    (r'^model-report/', include('tendenci.libs.model_report.urls')),
)

# Tendenci Patterns
urlpatterns += patterns('',
    url(r'^$', 'tendenci.core.base.views.homepage', name="home"),

    #Reports:
    (r'^metrics/', include('tendenci.apps.metrics.urls')),
    url(r'^users/reports/users-activity-top10/$', 'tendenci.apps.profiles.views.user_activity_report', name='reports-user-activity'),
    url(r'^users/reports/active-logins/$', 'tendenci.apps.profiles.views.user_access_report', name='reports-user-access'),
    url(r'^users/reports/not-in-groups/$', 'tendenci.apps.profiles.views.users_not_in_groups', name='reports-users-not-in-groups'),
    url(r'^users/reports/admin/$', 'tendenci.apps.profiles.views.admin_users_report', name='reports-admin-users'),
    url(r'^users/reports/users-added/$', 'tendenci.apps.user_groups.views.users_added_report', {'kind': 'added'}, name='reports-user-added'),
    url(r'^users/reports/contacts-referral/$', 'tendenci.apps.user_groups.views.users_added_report', {'kind': 'referral'}, name='reports-contacts-referral'),

    (r'^notifications/', include('tendenci.apps.notifications.urls')),
    (r'^base/', include('tendenci.core.base.urls')),
    (r'^tags/', include('tendenci.core.tags.urls')),
    (r'^avatar/', include('avatar.urls')),
    (r'^dashboard/', include('tendenci.apps.dashboard.urls')),
    (r'^categories/', include('tendenci.core.categories.urls')),
    (r'^invoices/', include('tendenci.apps.invoices.urls')),
    (r'^py/', include('tendenci.addons.make_payments.urls')),
    (r'^payments/', include('tendenci.core.payments.urls')),
    (r'^rp/', include('tendenci.addons.recurring_payments.urls')),
    (r'^accountings/', include('tendenci.apps.accountings.urls')),
    (r'^emails/', include('tendenci.core.emails.urls')),
    (r'^rss/', include('tendenci.core.rss.urls')),
    (r'^imports/', include('tendenci.core.imports.urls')),
    #(r'^donations/', include('donations.urls')),
    (r'^settings/', include('tendenci.core.site_settings.urls')),
    (r'^accounts/', include('tendenci.apps.accounts.urls')),
    (r'^search/', include('tendenci.apps.search.urls')),
    (r'^event-logs/', include('tendenci.core.event_logs.urls')),
    (r'^theme-editor/', include('tendenci.apps.theme_editor.urls')),
    (r'^exports/', include('tendenci.core.exports.urls')),
    (r'^ics/', include('tendenci.addons.events.ics.urls')),
    (r'^boxes/', include('tendenci.apps.boxes.urls')),
    (r'^sitemap.xml', include('tendenci.core.sitemaps.urls')),
    (r'^404/', include('tendenci.core.handler404.urls')),

    (r'^subscribers/', include('tendenci.apps.subscribers.urls')),
    (r'^redirects/', include('tendenci.apps.redirects.urls')),
    (r'^mobile/', include('tendenci.core.mobile.urls')),
    (r'^campaign_monitor/', include('tendenci.addons.campaign_monitor.urls')),
    (r'^wp_importer/', include('tendenci.apps.wp_importer.urls')),
    (r'^wp_exporter/', include('tendenci.apps.wp_exporter.urls')),
    (r'^discounts/', include('tendenci.apps.discounts.urls')),
    (r'^versions/', include('tendenci.core.versions.urls')),
    (r'^reports/', include('tendenci.apps.reports.urls')),
    url(r'social_auth/', include('tendenci.addons.social_auth.urls')),
    url(r'navs/', include('tendenci.apps.navs.urls')),
    url(r'tendenci/', include('tendenci.addons.tendenci_guide.urls')),
    url(r'^api_tasty/', include('tendenci.core.api_tasty.urls')),

    # third party (inside environment)
    (r'^tinymce/', include('tendenci.libs.tinymce.urls')),
    (r'^captcha/', include('captcha.urls')),

    url(r'^sitemap/$', direct_to_template, {"template": "site_map.html", }, name="site_map"),
    url(r'^robots.txt', 'tendenci.core.base.views.robots_txt', name="robots"),
    url(r'^(?P<file_name>[\w-]+\.[\w]{2,4})$', 'tendenci.core.base.views.base_file'),

    # legacy redirects
    url(r'^login/$', redirect_to, {'url': '/accounts/login/'}),

    url(r'^', include('tendenci.addons.articles.urls')),
    url(r'^', include('tendenci.addons.corporate_memberships.urls')),
    url(r'^', include('tendenci.addons.directories.urls')),
    url(r'^', include('tendenci.addons.events.urls')),
    url(r'^', include('tendenci.addons.help_files.urls')),
    url(r'^', include('tendenci.addons.jobs.urls')),
    url(r'^', include('tendenci.addons.locations.urls')),
    url(r'^', include('tendenci.addons.memberships.urls')),
    url(r'^', include('tendenci.addons.news.urls')),
    url(r'^', include('tendenci.addons.photos.urls')),
    url(r'^', include('tendenci.addons.resumes.urls')),
    url(r'^', include('tendenci.apps.contacts.urls')),
    url(r'^', include('tendenci.apps.contributions.urls')),
    url(r'^', include('tendenci.apps.entities.urls')),
    url(r'^', include('tendenci.apps.forms_builder.forms.urls')),
    url(r'^', include('tendenci.apps.pages.urls')),
    url(r'^', include('tendenci.apps.profiles.urls')),
    url(r'^', include('tendenci.apps.stories.urls')),
    url(r'^', include('tendenci.apps.user_groups.urls')),
    url(r'^', include('tendenci.core.files.urls')),
    url(r'^', include('tendenci.core.newsletters.urls')),
)

handler500 = 'tendenci.core.base.views.custom_error'


if hasattr(settings, 'USE_S3_STORAGE') and settings.USE_S3_STORAGE:
    urlpatterns += patterns('',
    # serve .less files - this is to resolve the cross domain issue for less js
    url(r'^(?P<path>.*)\.less$', 
        'tendenci.core.files.views.display_less',  name='less_file'),
    url(r'^static/(?P<path>.*)$',
            'tendenci.core.files.views.redirect_to_s3',
             {'file_type': 'static'},
                name='redirect_to_s3'),
    # this is basically for those images with relative urls in the theme .css files.
    url(r'^themes/(?P<path>.*)$',
            'tendenci.core.files.views.redirect_to_s3',
            {'file_type': 'themes'},
                name='redirect_to_s3'),
)

# serve static files
if settings.DEBUG:
    if not (hasattr(settings, 'USE_S3_STORAGE') and settings.USE_S3_STORAGE):
        urlpatterns += patterns('',
            (r'^static/(?P<path>.*)$',
                'django.views.static.serve',
                {'document_root': join(settings.TENDENCI_ROOT, 'static')}),

            (r'^plugin-media/(?P<plugin>[^/]+)/(?P<path>.*)$',
                'tendenci.core.base.views.plugin_static_serve'),
        )
        urlpatterns += patterns('',
            (r'^themes/(?P<path>.*)$',
                'django.views.static.serve',
                {'document_root': settings.THEMES_DIR, 'show_indexes': True}),
        )

# Favicon url to prevent 404 from some browsers.
urlpatterns += patterns('',
    (r'^(?P<path>favicon\.ico)$',
        'django.views.static.serve',
        {'document_root': join(settings.STATIC_ROOT, 'images'), 'show_indexes': True}),
)

# template tag testing environment
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^tag-test/$', direct_to_template, {"template": "tag_test.html", }, name="tag_test"),
    )

# Local url patterns for development
try:
    from local_urls import extra_patterns
    urlpatterns += extra_patterns
except ImportError:
    pass

#PLUGINS:
from tendenci.core.registry.utils import get_url_patterns
urlpatterns += get_url_patterns()

urlpatterns += patterns('', url(r'^en/$', redirect_to, {'url': '/accounts/login/'}),)

# tack on the pages pattern at the very end so let custom and software patterns
# happen first
pattern_pages = patterns('',
    # page view
    url(r'^(?P<slug>[\w\-\/]+)/$', 'tendenci.apps.pages.views.index', name="page"),  
)
urlpatterns += pattern_pages
