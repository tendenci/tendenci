from django.template import Library

from tendenci.apps.memberships.utils import get_membership_field_values

register = Library()


@register.inclusion_tag('memberships/search-per-app-member-line.html')
def render_member_row(membership, app_fields):
    field_values_list = get_membership_field_values(membership, app_fields)

    return {'membership': membership,
            'field_values_list': field_values_list}

@register.inclusion_tag("memberships/options.html", takes_context=True)
def membership_options(context, user, membership):
    context.update({
        "opt_object": membership,
        "user": user
    })
    return context


@register.inclusion_tag("memberships/nav.html", takes_context=True)
def membership_nav(context, user, membership=None):
    context.update({
        "nav_object" : membership,
        "user": user
    })
    return context


@register.inclusion_tag("memberships/search-form.html", takes_context=True)
def membership_search(context):
    return context


@register.inclusion_tag('memberships/renew-button.html', takes_context=True)
def renew_button(context):
    return context


@register.inclusion_tag("memberships/applications/render_membership_field.html")
def render_membership_field(request, field_obj,
                            user_form,
                            profile_form,
                            demographics_form,
                            membership_form,
                            education_form):
    field_pwd = None
    if field_obj.field_type == "section_break":
        field = None
    else:
        field_name = field_obj.field_name
        if field_name in membership_form.fields:
            field = membership_form[field_name]
        elif field_name in profile_form.field_names:
            field = profile_form[field_name]
        elif field_name in demographics_form.field_names:
            field = demographics_form[field_name]
        elif field_name in education_form.field_names:
            field = education_form[field_name]
        elif field_name in user_form.field_names:
            field = user_form[field_name]
            if field_obj.field_name == 'password':
                field_pwd = user_form['confirm_password']
        else:
            field = None

    return {'request': request, 'field_obj': field_obj,
            'field': field, 'field_pwd': field_pwd}


@register.filter
def get_actions(membership, user):
    """
    Returns a 2-tuple of membership
    actions available via super-user status.

    Example call:
        membership.get_actions|request.user
    """
    profile = getattr(user, 'profile')
    if profile and profile.is_superuser:
        return list(membership.get_actions(is_superuser=True).items())
    else:
        return list(membership.get_actions().items())


@register.inclusion_tag("memberships/top_nav_items.html", takes_context=True)
def membership_current_app(context, user, membership=None):
    context.update({
        "app_object" : membership,
        "user": user
    })
    return context

@register.simple_tag(takes_context=True)
def get_membership_app(context, app_id):
    """
    Get membership app by id.
    """
    from tendenci.apps.memberships.models import MembershipApp
    from tendenci.apps.perms.utils import has_perm
    
    request = context.get('request')
    if not has_perm(request.user, 'memberships.view_membershipapp'):
        return None

    try:
        app_id = int(app_id)
    except:
        return None
    [membership_app] = MembershipApp.objects.filter(id=app_id)[:1] or [None]
    return membership_app
