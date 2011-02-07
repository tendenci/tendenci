from django.template import Library

register = Library()

@register.inclusion_tag("corporate_memberships/render_corp_field.html")
def render_corp_field(request, field_obj, form):
    if field_obj.field_type == "section_break" or field_obj.field_type == "page_break":
        field = None
    else:
        field_name = field_obj.field_name
        if not field_name: 
            field_name = "field_%s" % field_obj.id
        # skip the form field generation if it's a display only field
        if not hasattr(field_obj, 'display_only'):
            field_obj.display_only = False
        if field_obj.display_only:
            field = None
        else:
            field = eval("form['%s']" % field_name)
    return {'request':request, 'field_obj':field_obj, 'field':field}


@register.inclusion_tag("corporate_memberships/nav.html", takes_context=True)
def corpmemb_nav(context, user, corp_memb=None):
    context.update({
        'nav_object': corp_memb,
        "user": user
    })
    return context

@register.inclusion_tag("corporate_memberships/options.html", takes_context=True)
def corpmemb_options(context, user, corp_memb):
    context.update({
        "opt_object": corp_memb,
        "user": user
    })
    return context

@register.inclusion_tag("corporate_memberships/search_form.html", takes_context=True)
def corp_memb_search(context):
    return context

@register.inclusion_tag("corporate_memberships/add_links.html", takes_context=True)
def corp_memb_render_add_links(context):
    from corporate_memberships.models import CorpApp
    corp_apps = CorpApp.objects.filter(status=1, status_detail='active')
    app_count = corp_apps.count()
    context.update({
        "corp_apps": corp_apps,
        'app_count': app_count
    })
    return context