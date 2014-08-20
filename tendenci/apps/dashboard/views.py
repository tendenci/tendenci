import simplejson
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.models import User
from dateutil import parser

from tendenci.apps.dashboard.models import DashboardStatType
from tendenci.core.event_logs.models import EventLog
from tendenci.core.perms.decorators import superuser_required
from tendenci.core.site_settings.models import Setting
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.theme.shortcuts import themed_response

@login_required
def index(request, template_name="dashboard/index.html"):
    profile_redirect = get_setting('site', 'global', 'profile_redirect')
    if profile_redirect and profile_redirect != '/dashboard' and not request.user.profile.is_superuser:
        return redirect(profile_redirect)

    # self signup  free trial version
    has_paid = True
    activate_url = ''
    expired = False
    expiration_dt = ''
    if get_setting('site', 'developer', 'partner') == 'Self-Signup' \
             and  get_setting('site', 'developer', 'freepaid') == 'free':
        has_paid = False
        activate_url = get_setting('site', 'developer', 'siteactivatepaymenturl')
        site_create_dt = get_setting('site', 'developer', 'sitecreatedt')

        if site_create_dt:
            site_create_dt = parser.parse(site_create_dt)
        else:
            # find the site create date in user's table
            u = User.objects.get(pk=1)
            site_create_dt = u.date_joined

        expiration_dt = site_create_dt + timedelta(days=30)

        now = datetime.now()
        if now >= expiration_dt:
            expired = True

    statistics = DashboardStatType.objects.filter(displayed=True)

    EventLog.objects.log()
    return render_to_response(template_name, {
        'has_paid': has_paid,
        'activate_url': activate_url,
        'expired': expired,
        'expiration_dt': expiration_dt,
        'statistics': statistics,
    }, context_instance=RequestContext(request))


@login_required
def new(request, template_name="dashboard/new.html"):

    if get_setting('module', 'dashboard', 'themeredirect'):
        redirect_setting = Setting.objects.get(scope_category='dashboard',
                                               name='themeredirect')
        redirect_setting.set_value(False)
        redirect_setting.save()
        return redirect('tendenci.apps.theme_editor.views.theme_picker')

    profile_redirect = get_setting('site', 'global', 'profile_redirect')
    if profile_redirect and profile_redirect != '/dashboard' and not request.user.profile.is_superuser:
        if "<username>" in profile_redirect:
            profile_redirect = profile_redirect.replace("<username>", request.user.username)
        return redirect(profile_redirect)

    if get_setting('site', 'global', 'groupdashboard'):
        group_dashboard_urls = filter(None, request.user.group_member \
                                                    .values_list('group__dashboard_url', flat=True))
        if group_dashboard_urls:
            url = group_dashboard_urls[0]
            return redirect(url)

    # self signup  free trial version
    has_paid = True
    activate_url = ''
    expired = False
    expiration_dt = ''
    if get_setting('site', 'developer', 'partner') == 'Self-Signup' \
             and  get_setting('site', 'developer', 'freepaid') == 'free':
        has_paid = False
        activate_url = get_setting('site', 'developer', 'siteactivatepaymenturl')
        site_create_dt = get_setting('site', 'developer', 'sitecreatedt')

        if site_create_dt:
            site_create_dt = parser.parse(site_create_dt)
        else:
            # find the site create date in user's table
            u = User.objects.get(pk=1)
            site_create_dt = u.date_joined

        expiration_dt = site_create_dt + timedelta(days=30)

        now = datetime.now()
        if now >= expiration_dt:
            expired = True

    statistics = DashboardStatType.objects.filter(displayed=True)

    EventLog.objects.log()
    return render_to_response(template_name, {
        'has_paid': has_paid,
        'activate_url': activate_url,
        'expired': expired,
        'expiration_dt': expiration_dt,
        'statistics': statistics,
    }, context_instance=RequestContext(request))


@superuser_required
def customize(request, template_name="dashboard/customize.html"):

    DashboardStatFormSet = modelformset_factory(
        DashboardStatType,
        exclude=('name',),
        extra=0
    )
    if request.method == "POST":
        formset = DashboardStatFormSet(request.POST)
        if formset.is_valid():
            formset.save()

            return redirect('dashboard')
    else:
        formset = DashboardStatFormSet(queryset=DashboardStatType.objects.all())

    return render_to_response(template_name, {
        'formset': formset,
    }, context_instance=RequestContext(request))
