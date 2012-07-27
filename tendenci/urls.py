from os.path import join
from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template, redirect_to
from django.contrib import admin

from tendenci.core.theme.utils import get_theme_root, get_theme, theme_choices
from tendenci.core.registry import autodiscover as reg_autodiscover

# load the apps that are in Django Admin
admin.autodiscover()

# load the app_registry
reg_autodiscover()

# Admin Patterns
urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)

# Tendenci Patterns
urlpatterns += patterns('',
    url(r'^$', 'tendenci.core.base.views.homepage', name="home"),

    #Reports:
    (r'^reports/', include('tendenci.apps.reports.urls')),
    (r'^metrics/', include('tendenci.contrib.metrics.urls')),
    url(r'^users/reports/users-activity-top10/$', 'tendenci.contrib.profiles.views.user_activity_report', name='reports-user-activity'),
    url(r'^users/reports/active-logins/$', 'tendenci.contrib.profiles.views.user_access_report', name='reports-user-access'),
    url(r'^users/reports/admin/$', 'tendenci.contrib.profiles.views.admin_users_report', name='reports-admin-users'),
    url(r'^users/reports/users-added/$', 'tendenci.contrib.user_groups.views.users_added_report', {'kind': 'added'}, name='reports-user-added'),
    url(r'^users/reports/contacts-referral/$', 'tendenci.contrib.user_groups.views.users_added_report', {'kind': 'referral'}, name='reports-contacts-referral'),

    (r'^notifications/', include('tendenci.contrib.notifications.urls')),
    (r'^base/', include('tendenci.core.base.urls')),
    (r'^avatar/', include('avatar.urls')),
    (r'^dashboard/', include('tendenci.contrib.dashboard.urls')),
    (r'^categories/', include('tendenci.core.categories.urls')),
    (r'^memberships/', include('tendenci.apps.memberships.urls')),
    (r'^corporatememberships/', include('tendenci.apps.corporate_memberships.urls')),
    (r'^entities/', include('tendenci.contrib.entities.urls')),
    (r'^pages/', include('tendenci.contrib.pages.urls')),
    (r'^users/', include('tendenci.contrib.profiles.urls')),
    (r'^photos/', include('tendenci.apps.photos.urls')),
    (r'^forms/', include('tendenci.contrib.forms_builder.forms.urls')),
    (r'^events/', include('tendenci.apps.events.urls')),
    (r'^profiles/', include('tendenci.contrib.profiles.urls')),
    (r'^groups/', include('tendenci.contrib.user_groups.urls')),
    (r'^stories/', include('tendenci.contrib.stories.urls')),
    (r'^invoices/', include('tendenci.contrib.invoices.urls')),
    (r'^py/', include('tendenci.apps.make_payments.urls')),
    (r'^payments/', include('tendenci.core.payments.urls')),
    (r'^accountings/', include('tendenci.contrib.accountings.urls')),
    (r'^emails/', include('tendenci.core.emails.urls')),
    (r'^rss/', include('tendenci.core.rss.urls')),
    (r'^imports/', include('tendenci.core.imports.urls')),
    #(r'^donations/', include('donations.urls')),
    (r'^news/', include('tendenci.apps.news.urls')),
    (r'^settings/', include('tendenci.core.site_settings.urls')),
    (r'^files/', include('tendenci.core.files.urls')),
    (r'^accounts/', include('tendenci.contrib.accounts.urls')),
    (r'^search/', include('tendenci.apps.search.urls')),
    (r'^event-logs/', include('tendenci.core.event_logs.urls')),
    (r'^contributions/', include('tendenci.contrib.contributions.urls')),
    (r'^theme-editor/', include('tendenci.contrib.theme_editor.urls')),
    (r'^exports/', include('tendenci.core.exports.urls')),
    (r'^boxes/', include('tendenci.contrib.boxes.urls')),
    (r'^sitemap.xml', include('tendenci.core.sitemaps.urls')),

    (r'^subscribers/', include('tendenci.contrib.subscribers.urls')),
    (r'^redirects/', include('tendenci.contrib.redirects.urls')),
    (r'^resumes/', include('tendenci.apps.resumes.urls')),
    (r'^mobile/', include('tendenci.core.mobile.urls')),
    (r'^campaign_monitor/', include('tendenci.apps.campaign_monitor.urls')),
    (r'^wp_importer/', include('tendenci.contrib.wp_importer.urls')),
    (r'^wp_exporter/', include('tendenci.contrib.wp_exporter.urls')),
    (r'^discounts/', include('tendenci.contrib.discounts.urls')),
    url(r'social_auth/', include('tendenci.apps.social_auth.urls')),
    url(r'navs/', include('tendenci.contrib.navs.urls')),
    url(r'tendenci/', include('tendenci.apps.tendenci_guide.urls')),
    url(r'^api_tasty/', include('tendenci.core.api_tasty.urls')),

    # third party (inside environment)
    (r'^tinymce/', include('tinymce.urls')),
    (r'^captcha/', include('captcha.urls')),

    url(r'^sitemap/$', direct_to_template, {"template": "site_map.html", }, name="site_map"),
    url(r'^robots.txt', 'tendenci.core.base.views.robots_txt', name="robots"),

    # legacy redirects
    url(r'^login/$', redirect_to, {'url': '/accounts/login/'}),
    
    # other t4 to t5 legacy redirects
    url(r'^en/', include('tendenci.apps.legacy.urls')),

    url(r'^', include('tendenci.contrib.contacts.urls')),
    #url(r'^', include('tendenci.apps.articles.urls')),
    url(r'^', include('tendenci.apps.jobs.urls')),
    url(r'^', include('tendenci.apps.directories.urls')),
    url(r'^', include('tendenci.apps.help_files.urls')),
    url(r'^', include('tendenci.apps.locations.urls')),
)

handler500 = 'apps.base.views.custom_error'

# serve static files
if settings.DEBUG:
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
from tendenci.contrib.pluginmanager import get_url_patterns
urlpatterns += get_url_patterns()

# tack on the pages pattern at the very end so let custom and software patterns
# happen first
pattern_pages = patterns('',
    # page view
    url(r'^(?P<slug>[\w\-\/]+)/$', 'tendenci.contrib.pages.views.index', name="page"),  
)
urlpatterns += pattern_pages
