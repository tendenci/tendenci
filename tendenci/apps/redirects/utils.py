from django.conf.urls import url, patterns
from django.utils.http import urlquote
from django.views.generic import RedirectView
from tendenci.apps.redirects.models import Redirect

def group_aruments(seq, group=254):
    """
        group the list into lists of 254 items each.

        This is due to argument restrictions in python.
        http://docs.djangoproject.com/en/dev/topics/http/urls/#patterns
    """
    return (seq[pos:pos + group] for pos in range(0, len(seq), group))

def get_redirect_patterns():
    """
        Gets the redirect patterns out of the database
        and assigns them to the django patterns object.
    """
    redirects = Redirect.objects.filter(status=True).order_by('uses_regex')
    url_patterns = []
    url_list = []
    for redirect in redirects:
        extra = {}

        # use urlquote so we can support '?' in the redirect
        if not redirect.uses_regex:
            pattern = r'^%s/?$' % urlquote(redirect.from_url)
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
            url_list.append(url(pattern, RedirectView.as_view(**extra)))
        else:
            url_list.append(url(pattern, RedirectView.as_view(**extra)))
    arg_groups = list(group_aruments(url_list))

    for args in arg_groups:
        url_patterns += patterns('',*args)

    return url_patterns
