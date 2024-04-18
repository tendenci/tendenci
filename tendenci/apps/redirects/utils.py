from urllib.parse import quote
from django.urls import re_path
from django.views.generic import RedirectView
from tendenci.apps.redirects.models import Redirect

def get_redirect_patterns():
    """
        Gets the redirect patterns out of the database
        and assigns them to the django patterns object.
    """
    redirects = Redirect.objects.filter(status=True).order_by('uses_regex')
    url_list = []
    for redirect in redirects:
        extra = {}

        # use urlquote so we can support '?' in the redirect
        if not redirect.uses_regex:
            pattern = r'^%s/?$' % quote(redirect.from_url)
        else:
            pattern = r'^%s/?$' % redirect.from_url

        if 'http' in redirect.to_url:
            extra.update({'url':'%s' % redirect.to_url})
        elif 'https' in redirect.to_url:
            extra.update({'url':'%s' % redirect.to_url})
        else:
            extra.update({'url':'/%s' % redirect.to_url})

        if redirect.http_status == 302:
            extra.update({'permanent': False})
            url_list.append(re_path(pattern, RedirectView.as_view(**extra)))
        else:
            url_list.append(re_path(pattern, RedirectView.as_view(**extra)))

    return url_list
