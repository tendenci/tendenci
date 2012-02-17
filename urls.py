from os.path import join
from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template, redirect_to
from django.conf import settings
from django.contrib import admin
from theme.utils import get_theme_root, get_theme, theme_choices
from registry import autodiscover as reg_autodiscover

# load the apps that are in Django Admin
admin.autodiscover()

# load the app_registry
reg_autodiscover()


urlpatterns = patterns('',
    url(r'^$', 'base.views.homepage', name="home"),

    #Reports:
    (r'^reports/', include('reports.urls')),
    (r'^metrics/', include('metrics.urls')),
    url(r'^event-logs/reports/summary/$', 'event_logs.views.event_summary_report', name='reports-events-summary'),
    url(r'^event-logs/reports/summary/([^/]+)/$', 'event_logs.views.event_source_summary_report', name='reports-events-source'),
    url(r'^users/reports/users-activity-top10/$', 'profiles.views.user_activity_report', name='reports-user-activity'),
    url(r'^users/reports/active-logins/$', 'profiles.views.user_access_report', name='reports-user-access'),
    url(r'^users/reports/admin/$', 'profiles.views.admin_users_report', name='reports-admin-users'),
    url(r'^users/reports/users-added/$', 'user_groups.views.users_added_report', {'kind': 'added'}, name='reports-user-added'),
    url(r'^users/reports/contacts-referral/$', 'user_groups.views.users_added_report', {'kind': 'referral'}, name='reports-contacts-referral'),
    url(r'^articles/reports/rank/$', 'articles.views.articles_report', name='reports-articles'),

    (r'^notifications/', include('notification.urls')),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^base/', include('base.urls')),
    (r'^avatar/', include('avatar.urls')),
    (r'^dashboard/', include('dashboard.urls')),
    (r'^categories/', include('categories.urls')),
    (r'^articles/', include('articles.urls')),
    (r'^memberships/', include('memberships.urls')),
    (r'^corporatememberships/', include('corporate_memberships.urls')),
    (r'^entities/', include('entities.urls')),
    (r'^locations/', include('locations.urls')),
    (r'^pages/', include('pages.urls')),
    (r'^users/', include('profiles.urls')),
    (r'^photos/', include('photos.urls')),
    (r'^forms/', include('forms_builder.forms.urls')),
    (r'^events/', include('events.urls')),
    (r'^profiles/', include('profiles.urls')),
    (r'^groups/', include('user_groups.urls')),
    (r'^stories/', include('stories.urls')),
    (r'^invoices/', include('invoices.urls')),
    (r'^py/', include('make_payments.urls')),
    (r'^payments/', include('payments.urls')),
    (r'^accountings/', include('accountings.urls')),
    (r'^emails/', include('emails.urls')),
    #(r'^newsletters/', include('newsletters.urls')),
    (r'^actions/', include('actions.urls')),
    (r'^rss/', include('rss.urls')),
    (r'^imports/', include('imports.urls')),
    #(r'^donations/', include('donations.urls')),
    (r'^news/', include('news.urls')),
    (r'^settings/', include('site_settings.urls')),
    (r'^files/', include('files.urls')),
    (r'^contacts/', include('contacts.urls')),
    (r'^accounts/', include('accounts.urls')),
    (r'^search/', include('search.urls')),
    (r'^event-logs/', include('event_logs.urls')),
    (r'^contributions/', include('contributions.urls')),
    (r'^theme-editor/', include('theme_editor.urls')),
    (r'^directories/', include('directories.urls')),
    (r'^contact/', include('form_builder.urls')),
    (r'^sitemap.xml', include('sitemaps.urls')),
    (r'^help-files/', include('help_files.urls')),
    (r'^subscribers/', include('subscribers.urls')),
    # third party (inside environment)
    (r'^tinymce/', include('tinymce.urls')),
    (r'^captcha/', include('captcha.urls')),
    (r'^redirects/', include('redirects.urls')),
    (r'^resumes/', include('resumes.urls')),
    (r'^mobile/', include('mobile.urls')),
    (r'^campaign_monitor/', include('campaign_monitor.urls')),
    (r'^wp_importer/', include('wp_importer.urls')),
    (r'^wp_exporter/', include('wp_exporter.urls')),
    (r'^discounts/', include('discounts.urls')),
    url(r'social_auth/', include('social_auth.urls')),
    url(r'plugin_builder/', include('plugin_builder.urls')),
    url(r'navs/', include('navs.urls')),
    url(r'tendenci/', include('tendenci_guide.urls')),
    url(r'^api_tasty/', include('api_tasty.urls')),


    url(r'^sitemap/$', direct_to_template, {"template": "site_map.html", }, name="site_map"),
    url(r'^robots.txt', direct_to_template, {"template": "robots.txt", }, name="robots"),

    # legacy redirects
    url(r'^login/$', redirect_to, {'url': '/accounts/login/'}),
    
    # other t4 to t5 legacy redirects
    url(r'^en/', include('legacy.urls')),
)

handler500 = 'base.views.custom_error'

# serve static files
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$',
            'django.views.static.serve',
            {'document_root': join(settings.PROJECT_ROOT, 'site_media')}),

        (r'^plugin-media/(?P<plugin>[^/]+)/(?P<path>.*)$',
            'base.views.plugin_static_serve'),
    )
    urlpatterns += patterns('',
        (r'^themes/(?P<path>.*)$',
            'django.views.static.serve',
            {'document_root': settings.THEME_DIR, 'show_indexes': True}),
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
import pluginmanager
urlpatterns += pluginmanager.get_url_patterns()

# tack on the pages pattern at the very end so let custom and software patterns
# happen first
pattern_pages = patterns('',
    # page view
    url(r'^(?P<slug>[\w\-\/]+)/$', 'pages.views.index', name="page"),  
)
urlpatterns += pattern_pages
