from django.template import Library

register = Library()

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

@register.inclusion_tag("memberships/entries/options.html", takes_context=True)
def entry_options(context, user, entry):
    context.update({
        "opt_object": entry,
        "user": user
    })
    return context

@register.inclusion_tag("memberships/entries/nav.html", takes_context=True)
def entry_nav(context, user, entry=None):
    context.update({
        "nav_object" : entry,
        "user": user
    })
    return context

@register.inclusion_tag("memberships/entries/search-form.html", takes_context=True)
def entry_search(context):
    return context

@register.inclusion_tag('memberships/renew-button.html', takes_context=True)
def renew_button(context):
    return context


@register.inclusion_tag("memberships/applications/render_membership_field.html")
def render_membership_field(request, field_obj,
                            user_form,
                            profile_form,
                            demographics_form,
                            membership_form):
    field_pwd = None
    if field_obj.field_type == "section_break":
        field = None
    else:
        field_name = field_obj.field_name
        if field_name in membership_form.field_names:
            field = membership_form[field_name]
        elif field_name in profile_form.field_names:
            field = profile_form[field_name]
        elif field_name in demographics_form.field_names:
            field = demographics_form[field_name]
        elif field_name in user_form.field_names:
            field = user_form[field_name]
            if field_obj.field_name == 'password':
                field_pwd = user_form['confirm_password']
        else:
            field = None

    return {'request': request, 'field_obj': field_obj,
            'field': field, 'field_pwd': field_pwd}
