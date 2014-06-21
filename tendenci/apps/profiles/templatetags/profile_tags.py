from django.template import Library
from django.contrib.auth.models import User

from avatar import AVATAR_DEFAULT_URL, AVATAR_GRAVATAR_BACKUP, AVATAR_GRAVATAR_DEFAULT
from avatar.templatetags.avatar_tags import avatar_url


register = Library()

@register.inclusion_tag("profiles/nav.html", takes_context=True)
def users_nav(context, user_current, user_this):
    if user_this:
        try:
            profile_this = user_this.get_profile()
        except:
            profile_this = None
    else:
        profile_this = None
    context.update({
        "user_current":user_current,
        "user_this": user_this,
        "nav_object": profile_this,
        "profile":profile_this
    })

    return context

@register.inclusion_tag("profiles/options.html", takes_context=True)
def users_options(context, user_current, user_this):
    if user_this:
        try:
            profile_this = user_this.get_profile()
        except:
            profile_this = None
    else:
        profile_this = None
    context.update({
        "user_current":user_current,
        "user_this": user_this,
        "profile":profile_this
    })
    return context

@register.inclusion_tag("profiles/search-form.html", takes_context=True)
def profile_search(context):
    return context

@register.inclusion_tag("profiles/meta.html", takes_context=True)
def profile_meta(context, detail_view=None):
    context.update({
        "detail_view":detail_view,
    })
    return context


@register.inclusion_tag("profiles/similar_profile_items.html", takes_context=True)
def similar_profile_items(context, users):
    context.update({
        "users": users,
    })
    return context

@register.inclusion_tag("profiles/merge_detail.html", takes_context=True)
def merge_detail(context, profile):
    context.update({
        "profile": profile,
    })
    return context

@register.simple_tag
def has_avatar(user, size=88):
    """
    Used to pull the avatar from a user profile. If an image has not been set
    no image will be returned.

    Usage::

        {% has_avatar model.user [size] %}

    Be sure to attach .user to an object that  contains a user relationship.
    Example::

    {% for officer in officers %}
        {% has_avatar officer.user 64 %}
    {% endfor %}

    This will return an avatar image that is 64x64 pixels.

    Note: This uses the 'django-avatar' package: https://github.com/jezdez/django-avatar
    """
    if not isinstance(user, User):
        try:
            user = User.objects.get(username=user)
            alt = unicode(user)
            url = avatar_url(user, size)
        except User.DoesNotExist:
            url = AVATAR_DEFAULT_URL
            alt = _("Default Avatar")
    else:
        alt = unicode(user)
        url = avatar_url(user, size)
    if url == AVATAR_DEFAULT_URL:
        return ""

    title = "%s profile" % alt
    if len(alt) > 123:
        alt = alt[:123]
    if len(title) > 123:
        title = title[:123]
    return """<img src="%s" alt="%s" title="%s" width="%s" height="%s" />""" % (url, alt, title,
          size, size)
