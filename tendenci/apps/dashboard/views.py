from datetime import datetime, timedelta
from dateutil import parser

from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory
from django.shortcuts import redirect
from django.contrib.auth.models import User

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.dashboard.models import DashboardStatType
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.perms.decorators import superuser_required
from tendenci.apps.site_settings.models import Setting
from tendenci.apps.site_settings.utils import get_setting


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
    return render_to_resp(request=request, template_name=template_name, context={
        'has_paid': has_paid,
        'activate_url': activate_url,
        'expired': expired,
        'expiration_dt': expiration_dt,
        'statistics': statistics,
    })


@login_required
def new(request, template_name="dashboard/new.html"):

    if get_setting('module', 'dashboard', 'themeredirect'):
        redirect_setting = Setting.objects.get(scope_category='dashboard',
                                               name='themeredirect')
        redirect_setting.set_value(False)
        redirect_setting.save()
        return redirect('theme_editor.picker')

    # Redirect to Group dashboard url if any
    if get_setting('site', 'global', 'groupdashboard') and not request.user.profile.is_superuser:
        group_dashboard_urls = [m for m in request.user.group_member
                                                    .values_list('group__dashboard_url', flat=True) if m]
        if group_dashboard_urls:
            url = group_dashboard_urls[0]
            return redirect(url)

    # Redirect to the url speficied in the Profile Redirect setting if any
    profile_redirect = get_setting('site', 'global', 'profile_redirect')
    if profile_redirect and profile_redirect != '/dashboard' and not request.user.profile.is_superuser:
        if "<username>" in profile_redirect:
            profile_redirect = profile_redirect.replace("<username>", request.user.username)
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
    return render_to_resp(request=request, template_name=template_name, context={
        'has_paid': has_paid,
        'activate_url': activate_url,
        'expired': expired,
        'expiration_dt': expiration_dt,
        'statistics': statistics,
    })


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

    return render_to_resp(request=request, template_name=template_name, context={
        'formset': formset,
    })
