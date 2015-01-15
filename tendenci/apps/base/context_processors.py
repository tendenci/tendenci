from datetime import datetime

from django.conf import settings

from tendenci.apps.site_settings.utils import get_setting


def static_url(request):
    return {'STATIC_URL': settings.STATIC_URL, 'LOCAL_STATIC_URL': settings.LOCAL_STATIC_URL, 'STOCK_STATIC_URL': settings.STOCK_STATIC_URL, 'TINYMCE_JS_URL': settings.TINYMCE_JS_URL}


def index_update_note(request):
    return {'INDEX_UPDATE_NOTE': settings.INDEX_UPDATE_NOTE}


def today(request):
    return {'TODAY': datetime.today()}


def newrelic(request):
    """ newrelic removed due to increase of timeouts """
    return {
        'NEW_RELIC_HEADER': "",
        'NEW_RELIC_FOOTER': "",
    }


def site_admin_email(request):
    return {'SITE_ADMIN_EMAIL': get_setting('site', 'global', 'admincontactemail')}


def user_classification(request):
    data = {
    'USER_IS_NORMAL' : True,
    'USER_IS_SUPERUSER' : False,
    'USER_IS_MEMBER': False,
    'USER_IS_MEMBER_ACTIVE': False,
    'USER_IS_MEMBER_EXPIRED': False
    }
    if hasattr(request.user, 'profile') and request.user.profile.is_superuser:
        data.update({'USER_IS_SUPERUSER': True})
    elif hasattr(request.user, 'memberships'):
        active_memberships = request.user.membershipdefault_set.filter(
            status=True, status_detail__iexact='active'
        )
        inactive_memberships = request.user.membershipdefault_set.filter(
            status=True, status_detail__iexact='inactive'
        )
        data.update({'USER_IS_MEMBER':True})
        if inactive_memberships.exists() > 0:
            data.update({'USER_IS_MEMBER_EXPIRED': True})
        elif active_memberships.exists() > 0:
            data.update({'USER_IS_MEMBER_ACTIVE': True})

    return data


def display_name(request):
    if request.user.is_authenticated():
        if request.user.first_name:
            return {'DISPLAY_NAME': request.user.first_name}
        else:
            return {'DISPLAY_NAME': request.user.username}

    return {'DISPLAY_NAME': ''}
