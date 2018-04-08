from warnings import warn
from datetime import datetime
from django.conf import settings
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.theme.templatetags.static import static


def static_url(request):
    context = {}
    context['STOCK_STATIC_URL'] = settings.STOCK_STATIC_URL
    context['TINYMCE_JS_URL'] = static(settings.TINYMCE_JS_URL)

    # Backward compatibility for old themes
    def warn_static_url(value=settings.STATIC_URL):
        warn("{{ STATIC_URL }}<path> is deprecated, use {% static '<path>' %} instead", DeprecationWarning)
        return value
    context['STATIC_URL'] = warn_static_url
    def warn_local_static_url(value=settings.LOCAL_STATIC_URL):  # noqa: E306
        warn("{{ LOCAL_STATIC_URL }}<path> is deprecated, use {% local_static '<path>' %} instead", DeprecationWarning)
        return value
    context['LOCAL_STATIC_URL'] = warn_local_static_url

    return context


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
    if request.user.is_authenticated:
        if request.user.first_name:
            return {'DISPLAY_NAME': request.user.first_name}
        else:
            return {'DISPLAY_NAME': request.user.username}

    return {'DISPLAY_NAME': ''}
