from os.path import join
from django.urls import path, re_path, include
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
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
]

#report patterns
urlpatterns += [
    path('model-report/', include('tendenci.libs.model_report.urls')),
]

# Tendenci Patterns
urlpatterns += [
    re_path(r'^$', base_views.homepage, name="home"),

    #Reports:
    re_path(r'^metrics/', include('tendenci.apps.metrics.urls')),
    re_path(r'^users/reports/users-activity-top10/$', profiles_views.user_activity_report, name='reports-user-activity'),
    re_path(r'^users/reports/active-logins/$', profiles_views.user_access_report, name='reports-user-access'),
    re_path(r'^users/reports/not-in-groups/$', profiles_views.users_not_in_groups, name='reports-users-not-in-groups'),
    re_path(r'^users/reports/admin/$', profiles_views.admin_users_report, name='reports-admin-users'),
    re_path(r'^users/reports/users-added/$', user_groups_views.users_added_report, {'kind': 'added'}, name='reports-user-added'),
    re_path(r'^users/reports/contacts-referral/$', user_groups_views.users_added_report, {'kind': 'referral'}, name='reports-contacts-referral'),

    re_path(r'^notifications/', include('tendenci.apps.notifications.urls')),
    re_path(r'^base/', include('tendenci.apps.base.urls')),
    re_path(r'^tags/', include('tendenci.apps.tags.urls')),
    re_path(r'^dashboard/', include('tendenci.apps.dashboard.urls')),
    re_path(r'^categories/', include('tendenci.apps.categories.urls')),
    re_path(r'^invoices/', include('tendenci.apps.invoices.urls')),
    re_path(r'^py/', include('tendenci.apps.make_payments.urls')),
    re_path(r'^payments/', include('tendenci.apps.payments.urls')),
    re_path(r'^rp/', include('tendenci.apps.recurring_payments.urls')),
    re_path(r'^accountings/', include('tendenci.apps.accountings.urls')),
    re_path(r'^emails/', include('tendenci.apps.emails.urls')),
    re_path(r'^rss/', include('tendenci.apps.rss.urls')),
    re_path(r'^imports/', include('tendenci.apps.imports.urls')),
    #re_path(r'^donations/', include('donations.urls')),
    re_path(r'^settings/', include('tendenci.apps.site_settings.urls')),
    re_path(r'^accounts/', include('tendenci.apps.accounts.urls')),
    re_path(r'^search/', include('tendenci.apps.search.urls')),
    re_path(r'^event-logs/', include('tendenci.apps.event_logs.urls')),
    re_path(r'^theme-editor/', include('tendenci.apps.theme_editor.urls')),
    re_path(r'^exports/', include('tendenci.apps.exports.urls')),
    re_path(r'^ics/', include('tendenci.apps.events.ics.urls')),
    re_path(r'^boxes/', include('tendenci.apps.boxes.urls')),
    re_path(r'^sitemap.xml', include('tendenci.apps.sitemaps.urls')),
    re_path(r'^404/', include('tendenci.apps.handler404.urls')),

    re_path(r'^redirects/', include('tendenci.apps.redirects.urls')),
    re_path(r'^mobile/', include('tendenci.apps.mobile.urls')),
    re_path(r'^campaign_monitor/', include('tendenci.apps.campaign_monitor.urls')),
    re_path(r'^discounts/', include('tendenci.apps.discounts.urls')),
    re_path(r'^versions/', include('tendenci.apps.versions.urls')),
    re_path(r'^reports/', include('tendenci.apps.reports.urls')),
    #re_path(r'social_auth/', include('tendenci.apps.social_auth.urls')),  # Does not support Python 3
    re_path(r'navs/', include('tendenci.apps.navs.urls')),
    re_path(r'tendenci/', include('tendenci.apps.tendenci_guide.urls')),
    re_path(r'^api_tasty/', include('tendenci.apps.api_tasty.urls')),
    re_path(r'^forums/', include('tendenci.apps.forums.urls')),

    # third party (inside environment)
    re_path(r'^tinymce/', include('tendenci.libs.tinymce.urls')),
    re_path(r'^captcha/', include('captcha.urls')),

    re_path(r'^sitemap/$', TemplateView.as_view(template_name='site_map.html'), name="site_map"),
    re_path(r'^robots.txt', base_views.robots_txt, name="robots"),
    re_path(r'^(?P<file_name>[\w-]+\.[\w]{2,4})$', base_views.base_file),

    # legacy redirects
    re_path(r'^login/$', RedirectView.as_view(url='/accounts/login/', permanent=True)),

    re_path(r'^', include('tendenci.apps.articles.urls')),
    re_path(r'^', include('tendenci.apps.corporate_memberships.urls')),
    re_path(r'^', include('tendenci.apps.directories.urls')),
    re_path(r'^', include('tendenci.apps.events.urls')),
    re_path(r'^', include('tendenci.apps.help_files.urls')),
    re_path(r'^', include('tendenci.apps.jobs.urls')),
    re_path(r'^', include('tendenci.apps.locations.urls')),
    re_path(r'^', include('tendenci.apps.memberships.urls')),
    re_path(r'^', include('tendenci.apps.news.urls')),
    re_path(r'^', include('tendenci.apps.photos.urls')),
    re_path(r'^', include('tendenci.apps.resumes.urls')),
    re_path(r'^', include('tendenci.apps.contacts.urls')),
    re_path(r'^', include('tendenci.apps.contributions.urls')),
    re_path(r'^', include('tendenci.apps.entities.urls')),
    re_path(r'^', include('tendenci.apps.forms_builder.forms.urls')),
    re_path(r'^', include('tendenci.apps.pages.urls')),
    re_path(r'^', include('tendenci.apps.profiles.urls')),
    re_path(r'^', include('tendenci.apps.stories.urls')),
    re_path(r'^', include('tendenci.apps.user_groups.urls')),
    re_path(r'^', include('tendenci.apps.files.urls')),
    re_path(r'^', include('tendenci.apps.newsletters.urls')),

    re_path(r'^', include('tendenci.apps.committees.urls')),
    re_path(r'^', include('tendenci.apps.chapters.urls')),
    re_path(r'^', include('tendenci.apps.case_studies.urls')),
    re_path(r'^', include('tendenci.apps.donations.urls')),
    re_path(r'^', include('tendenci.apps.speakers.urls')),
    re_path(r'^', include('tendenci.apps.staff.urls')),
    re_path(r'^', include('tendenci.apps.studygroups.urls')),
    re_path(r'^', include('tendenci.apps.videos.urls')),
    re_path(r'^', include('tendenci.apps.testimonials.urls')),
    re_path(r'^', include('tendenci.apps.social_services.urls')),

    re_path(r'^explorer/', include('explorer.urls')),
    re_path(r'^explorer/', include('tendenci.apps.explorer_extensions.urls')),
]

if not settings.USE_S3_STORAGE:
    urlpatterns = [
        re_path(r'^media/(?P<path>.*)$', static.serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
        re_path(r'^static/(?P<path>.*)$', static.serve, {
            'document_root': settings.STATIC_ROOT,
        }),
        re_path(r'^themes/(?P<path>.*)$', static.serve, {
            'document_root': settings.THEMES_DIR,
        }),
    ] + urlpatterns
    if settings.DEBUG:
        urlpatterns = [
            re_path(r'^plugin-media/(?P<plugin>[^/]+)/(?P<path>.*)$',
                base_views.plugin_static_serve),
        ] + urlpatterns

if settings.USE_S3_STORAGE:
    urlpatterns = [
        # serve .less files - this is to resolve the cross domain issue for less js
        re_path(r'^(?P<path>.*)\.less$',
            files_views.display_less,  name='less_file'),
        re_path(r'^static/(?P<path>.*)$',
                files_views.redirect_to_s3,
                 {'file_type': 'static'},
                    name='redirect_to_s3'),
        # this is basically for those images with relative urls in the theme .css files.
        re_path(r'^themes/(?P<path>.*)$',
                files_views.redirect_to_s3,
                {'file_type': 'themes'},
                    name='redirect_to_s3'),
    ] + urlpatterns

# Favicon url to prevent 404 from some browsers.
urlpatterns += [
    re_path(r'^(?P<path>favicon\.ico)$',
        static.serve,
        {'document_root': join(settings.STATIC_ROOT, 'images'), 'show_indexes': True}),
]

# template tag testing environment
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^tag-test/$', TemplateView.as_view(template_name='tag_test.html'), name="tag_test"),
    ]

#PLUGINS:
urlpatterns += get_url_patterns()

urlpatterns += [re_path(r'^en/$', RedirectView.as_view(url='/accounts/login/', permanent=True)),]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ]

# tack on the pages pattern at the very end so let custom and software patterns
# happen first
pattern_pages = [
    # page view
    re_path(r'^(?P<slug>[\w\-\/]+)/$', pages_views.index, name="page"),
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
