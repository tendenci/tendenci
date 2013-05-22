from django.template import Node, Variable, Library
from tendenci.core.base.utils import tcurrency

register = Library()


@register.inclusion_tag(
        "corporate_memberships/applications/render_corpmembership_field.html")
def render_corpmembership_field(request, field_obj,
                                corpprofile_form,
                            corpmembership_form):
    if field_obj.field_type == "section_break":
        field = None
    else:
        field_name = field_obj.field_name
        if field_name in corpprofile_form.field_names \
                and not field_obj.display_only:
            field = corpprofile_form[field_name]
        elif field_name in corpmembership_form.field_names \
                and not field_obj.display_only:
            field = corpmembership_form[field_name]
        else:
            field = None

    return {'request': request, 'field_obj': field_obj,
            'field': field}


@register.simple_tag
def individual_pricing_desp(corp_membership):
    """
    Return the description of pricing for the individual memberships
    joining under this corp_membership.
    """
    description = ''
    if corp_membership:
        corporate_type = corp_membership.corporate_membership_type
        membership_type = corporate_type.membership_type
        admin_fee = membership_type.admin_fee
        if not admin_fee:
            admin_fee = 0

        if not (membership_type.price + admin_fee):
            membership_price = 'free'
        else:
            membership_price = tcurrency(membership_type.price)
            if membership_type.admin_fee:
                membership_price = '%s + %s' % (
                                    membership_price,
                                    tcurrency(membership_type.admin_fee))

        threshold = corporate_type.apply_threshold
        threshold_limit = corporate_type.individual_threshold
        threshold_price = corporate_type.individual_threshold_price
        if not threshold_price:
            threshold_price = 'free'
        else:
            threshold_price = tcurrency(threshold_price)

        if threshold and threshold_limit > 0:
            description += 'first %d %s, ' % (
                                    threshold_limit,
                                    threshold_price
                                    )
            description += 'then %s ' % membership_price
        else:
            description += '%s ' % membership_price
    return description


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
            field = form[field_name]
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


@register.inclusion_tag("corporate_memberships/applications/search_form.html", takes_context=True)
def corpmembership_search(context):
    return context


@register.inclusion_tag("corporate_memberships/search_form.html", takes_context=True)
def corp_memb_search(context):
    return context

@register.inclusion_tag("corporate_memberships/add_links.html", takes_context=True)
def corp_memb_render_add_links(context):
    from tendenci.addons.corporate_memberships.models import CorpApp
    corp_apps = CorpApp.objects.filter(status=True, status_detail='active')
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

