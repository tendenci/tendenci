from django.template import Node, Variable, Library

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


class AllowViewCorpNode(Node):
    def __init__(self, corp_memb, user, context_var):
        self.corp_memb = corp_memb
        self.user = user
        self.var_name = context_var
        
    def resolve(self, var, context):
        return Variable(var).resolve(context)
        
    def render(self, context):
        corp_memb = self.resolve(self.corp_memb, context)
        user = self.resolve(self.user, context)

        boo = corp_memb.allow_view_by(user)
    
        if self.var_name:
            context[self.var_name] = boo
            return ""
        else:
            return boo

@register.tag
def allow_view_corp(parser, token):
    """
        {% allow_view_corp corp_memb user as allow_view %}
    """
    bits  = token.split_contents()
    
    try: corp_memb = bits[1]
    except: corp_memb = None
    
    try: user = bits[2]
    except: user = None
    
    if len(bits) >= 5:
        context_var = bits[4]
    else:
        context_var = None
    return AllowViewCorpNode(corp_memb, user, context_var=context_var)


class AllowEditCorpNode(Node):
    def __init__(self, corp_memb, user, context_var):
        self.corp_memb = corp_memb
        self.user = user
        self.var_name = context_var
        
    def resolve(self, var, context):
        return Variable(var).resolve(context)
        
    def render(self, context):
        corp_memb = self.resolve(self.corp_memb, context)
        user = self.resolve(self.user, context)

        boo = corp_memb.allow_edit_by(user)
    
        if self.var_name:
            context[self.var_name] = boo
            return ""
        else:
            return boo

@register.tag
def allow_edit_corp(parser, token):
    """
        {% allow_edit_corp corp_memb user as allow_edit %}
    """
    bits  = token.split_contents()
    
    try: corp_memb = bits[1]
    except: corp_memb = None
    
    try: user = bits[2]
    except: user = None
    
    if len(bits) >= 5:
        context_var = bits[4]
    else:
        context_var = None
    return AllowEditCorpNode(corp_memb, user, context_var=context_var)

