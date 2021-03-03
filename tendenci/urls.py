from os.path import join
from django.conf.urls import url, include
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views import static
from django.views.generic import TemplateView, RedirectView
from django.contrib import admin
from tendenci.libs.model_report import report
from tendenci.apps.registry.register import autodiscover as registry_autodiscover
from tendenci.apps.registry.utils import get_url_patterns
from tendenci.apps.base import views as base_views
from tendenci.apps.profiles import views as profiles_views
from tendenci.apps.user_groups import views as user_groups_views
from tendenci.apps.files import views as files_views
from tendenci.apps.pages import views as pages_views


registry_autodiscover()

# django model report
report.autodiscover()

handler500 = 'tendenci.apps.base.views.custom_error'


# Admin Patterns
urlpatterns = [
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
]

#report patterns
urlpatterns += [
    url(r'^model-report/', include('tendenci.libs.model_report.urls')),
]

# Tendenci Patterns
urlpatterns += [
    url(r'^$', base_views.homepage, name="home"),

    #Reports:
    url(r'^metrics/', include('tendenci.apps.metrics.urls')),
    url(r'^users/reports/users-activity-top10/$', profiles_views.user_activity_report, name='reports-user-activity'),
    url(r'^users/reports/active-logins/$', profiles_views.user_access_report, name='reports-user-access'),
    url(r'^users/reports/not-in-groups/$', profiles_views.users_not_in_groups, name='reports-users-not-in-groups'),
    url(r'^users/reports/admin/$', profiles_views.admin_users_report, name='reports-admin-users'),
    url(r'^users/reports/users-added/$', user_groups_views.users_added_report, {'kind': 'added'}, name='reports-user-added'),
    url(r'^users/reports/contacts-referral/$', user_groups_views.users_added_report, {'kind': 'referral'}, name='reports-contacts-referral'),

    url(r'^notifications/', include('tendenci.apps.notifications.urls')),
    url(r'^base/', include('tendenci.apps.base.urls')),
    url(r'^tags/', include('tendenci.apps.tags.urls')),
    url(r'^dashboard/', include('tendenci.apps.dashboard.urls')),
    url(r'^categories/', include('tendenci.apps.categories.urls')),
    url(r'^invoices/', include('tendenci.apps.invoices.urls')),
    url(r'^py/', include('tendenci.apps.make_payments.urls')),
    url(r'^payments/', include('tendenci.apps.payments.urls')),
    url(r'^rp/', include('tendenci.apps.recurring_payments.urls')),
    url(r'^accountings/', include('tendenci.apps.accountings.urls')),
    url(r'^emails/', include('tendenci.apps.emails.urls')),
    url(r'^rss/', include('tendenci.apps.rss.urls')),
    url(r'^imports/', include('tendenci.apps.imports.urls')),
    #url(r'^donations/', include('donations.urls')),
    url(r'^settings/', include('tendenci.apps.site_settings.urls')),
    url(r'^accounts/', include('tendenci.apps.accounts.urls')),
    url(r'^search/', include('tendenci.apps.search.urls')),
    url(r'^event-logs/', include('tendenci.apps.event_logs.urls')),
    url(r'^theme-editor/', include('tendenci.apps.theme_editor.urls')),
    url(r'^exports/', include('tendenci.apps.exports.urls')),
    url(r'^ics/', include('tendenci.apps.events.ics.urls')),
    url(r'^boxes/', include('tendenci.apps.boxes.urls')),
    url(r'^sitemap.xml', include('tendenci.apps.sitemaps.urls')),
    url(r'^404/', include('tendenci.apps.handler404.urls')),

    url(r'^redirects/', include('tendenci.apps.redirects.urls')),
    url(r'^mobile/', include('tendenci.apps.mobile.urls')),
    url(r'^campaign_monitor/', include('tendenci.apps.campaign_monitor.urls')),
    url(r'^discounts/', include('tendenci.apps.discounts.urls')),
    url(r'^versions/', include('tendenci.apps.versions.urls')),
    url(r'^reports/', include('tendenci.apps.reports.urls')),
    #url(r'social_auth/', include('tendenci.apps.social_auth.urls')),  # Does not support Python 3
    url(r'navs/', include('tendenci.apps.navs.urls')),
    url(r'tendenci/', include('tendenci.apps.tendenci_guide.urls')),
    url(r'^api_tasty/', include('tendenci.apps.api_tasty.urls')),
    url(r'^forums/', include('tendenci.apps.forums.urls')),

    # third party (inside environment)
    url(r'^tinymce/', include('tendenci.libs.tinymce.urls')),
    url(r'^captcha/', include('captcha.urls')),

    url(r'^sitemap/$', TemplateView.as_view(template_name='site_map.html'), name="site_map"),
    url(r'^robots.txt', base_views.robots_txt, name="robots"),
    url(r'^(?P<file_name>[\w-]+\.[\w]{2,4})$', base_views.base_file),

    # legacy redirects
    url(r'^login/$', RedirectView.as_view(url='/accounts/login/', permanent=True)),

    url(r'^', include('tendenci.apps.articles.urls')),
    url(r'^', include('tendenci.apps.corporate_memberships.urls')),
    url(r'^', include('tendenci.apps.directories.urls')),
    url(r'^', include('tendenci.apps.events.urls')),
    url(r'^', include('tendenci.apps.help_files.urls')),
    url(r'^', include('tendenci.apps.jobs.urls')),
    url(r'^', include('tendenci.apps.locations.urls')),
    url(r'^', include('tendenci.apps.memberships.urls')),
    url(r'^', include('tendenci.apps.news.urls')),
    url(r'^', include('tendenci.apps.photos.urls')),
    url(r'^', include('tendenci.apps.resumes.urls')),
    url(r'^', include('tendenci.apps.contacts.urls')),
    url(r'^', include('tendenci.apps.contributions.urls')),
    url(r'^', include('tendenci.apps.entities.urls')),
    url(r'^', include('tendenci.apps.forms_builder.forms.urls')),
    url(r'^', include('tendenci.apps.pages.urls')),
    url(r'^', include('tendenci.apps.profiles.urls')),
    url(r'^', include('tendenci.apps.stories.urls')),
    url(r'^', include('tendenci.apps.user_groups.urls')),
    url(r'^', include('tendenci.apps.files.urls')),
    url(r'^', include('tendenci.apps.newsletters.urls')),

    url(r'^', include('tendenci.apps.committees.urls')),
    url(r'^', include('tendenci.apps.chapters.urls')),
    url(r'^', include('tendenci.apps.case_studies.urls')),
    url(r'^', include('tendenci.apps.donations.urls')),
    url(r'^', include('tendenci.apps.speakers.urls')),
    url(r'^', include('tendenci.apps.staff.urls')),
    url(r'^', include('tendenci.apps.studygroups.urls')),
    url(r'^', include('tendenci.apps.videos.urls')),
    url(r'^', include('tendenci.apps.testimonials.urls')),
    url(r'^', include('tendenci.apps.social_services.urls')),

    url(r'^explorer/', include('explorer.urls')),
    url(r'^explorer/', include('tendenci.apps.explorer_extensions.urls')),
]

if not settings.USE_S3_STORAGE:
    urlpatterns = [
        url(r'^media/(?P<path>.*)$', static.serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
        url(r'^static/(?P<path>.*)$', static.serve, {
            'document_root': settings.STATIC_ROOT,
        }),
        url(r'^themes/(?P<path>.*)$', static.serve, {
            'document_root': settings.THEMES_DIR,
        }),
    ] + urlpatterns
    if settings.DEBUG:
        urlpatterns = [
            url(r'^plugin-media/(?P<plugin>[^/]+)/(?P<path>.*)$',
                base_views.plugin_static_serve),
        ] + urlpatterns

if settings.USE_S3_STORAGE:
    urlpatterns = [
        # serve .less files - this is to resolve the cross domain issue for less js
        url(r'^(?P<path>.*)\.less$',
            files_views.display_less,  name='less_file'),
        url(r'^static/(?P<path>.*)$',
                files_views.redirect_to_s3,
                 {'file_type': 'static'},
                    name='redirect_to_s3'),
        # this is basically for those images with relative urls in the theme .css files.
        url(r'^themes/(?P<path>.*)$',
                files_views.redirect_to_s3,
                {'file_type': 'themes'},
                    name='redirect_to_s3'),
    ] + urlpatterns

# Favicon url to prevent 404 from some browsers.
urlpatterns += [
    url(r'^(?P<path>favicon\.ico)$',
        static.serve,
        {'document_root': join(settings.STATIC_ROOT, 'images'), 'show_indexes': True}),
]

# template tag testing environment
if settings.DEBUG:
    urlpatterns += [
        url(r'^tag-test/$', TemplateView.as_view(template_name='tag_test.html'), name="tag_test"),
    ]

#PLUGINS:
urlpatterns += get_url_patterns()

urlpatterns += [url(r'^en/$', RedirectView.as_view(url='/accounts/login/', permanent=True)),]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

# tack on the pages pattern at the very end so let custom and software patterns
# happen first
pattern_pages = [
    # page view
    url(r'^(?P<slug>[\w\-\/]+)/$', pages_views.index, name="page"),
]
urlpatterns += pattern_pages


# Allow custom URL patterns to be added between pre_urlpatterns and
# post_urlpatterns, but include both in urlpatterns in case this file is used
# by Django directly.
pre_urlpatterns = staticfiles_urlpatterns()
post_urlpatterns = urlpatterns
urlpatterns = pre_urlpatterns + post_urlpatterns


# Support removing URL patterns that have already been added.
# Only the first matching URL will be removed.

def remove_url_for_view(urlpatterns, view):
    for i, p in enumerate(urlpatterns):
        if hasattr(p, 'callback') and p.callback == view:
            del urlpatterns[i]
            break

def remove_url_for_include(urlpatterns, module_name):
    for i, p in enumerate(urlpatterns):
        if hasattr(p, 'urlconf_name') and p.urlconf_name == module_name:
            del urlpatterns[i]
            break

def remove_url_with_name(urlpatterns, name):
    for i, p in enumerate(urlpatterns):
        if p.name == name:
            del urlpatterns[i]
            break
