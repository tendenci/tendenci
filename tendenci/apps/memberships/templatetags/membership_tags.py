import random
from dateutil.parser import parse, ParserError

from django.contrib.auth.models import AnonymousUser, User
from django.template import Node, Library, TemplateSyntaxError, Variable

from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.memberships.utils import get_membership_field_values
from tendenci.apps.memberships.models import MembershipDefault
from tendenci.apps.base.template_tags import parse_tag_kwargs
from tendenci.apps.perms.utils import has_perm

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


class ListMembershipNode(Node):
    model = MembershipDefault

    def __init__(self, context_var, *args, **kwargs):
        self.context_var = context_var
        self.kwargs = kwargs

    def render(self, context):
        user = AnonymousUser()
        limit = 5
        order = '-join_dt'
        randomize = False
        new_member_only = False
        exclude_expired = False
        membership_type = None
        objects = []

        if 'user' in self.kwargs:
            try:
                user = Variable(self.kwargs['user'])
                user = user.resolve(context)
            except:
                user = self.kwargs['user']
                if user == "anon" or user == "anonymous":
                    user = AnonymousUser()
        else:
            # check the context for an already existing user
            # and see if it is really a user object
            if 'user' in context:
                if isinstance(context['user'], User):
                    user = context['user']

        # make sure this user has the adequate permission to view the members list
        membership_view_perms = get_setting('module', 'memberships', 'memberprotection')
        allow_view_members = False
        if user.is_authenticated:
            if user.is_superuser or has_perm(user, 'profiles.view_profile') or \
                (user.profile.is_member and membership_view_perms == 'all-members'):
                allow_view_members = True
        else:
            if membership_view_perms == 'public':
                allow_view_members = True   

        if allow_view_members:

            if 'random' in self.kwargs:
                randomize = bool(self.kwargs['random'])

            if 'limit' in self.kwargs:
                try:
                    limit = Variable(self.kwargs['limit'])
                    limit = int(limit.resolve(context))
                except:
                    limit = None

            if 'start_dt' in self.kwargs:
                try:
                    start_dt = Variable(self.kwargs['start_dt'])
                    start_dt = start_dt.resolve(context)
                    start_dt = parse(start_dt)
                except (ValueError, ParserError):
                    pass

            if 'order' in self.kwargs:
                try:
                    order = Variable(self.kwargs['order'])
                    order = order.resolve(context)
                except:
                    order = self.kwargs['order']

            if 'new_member_only' in self.kwargs:
                new_member_only = bool(self.kwargs['new_member_only'])
    
            if 'exclude_expired' in self.kwargs:
                exclude_expired = bool(self.kwargs['exclude_expired'])

            if 'membership_type' in self.kwargs:
                membership_type = self.kwargs['membership_type']

            items = MembershipDefault.objects.exclude(status_detail='archive')

            if start_dt:
                items = items.filter(join_dt__gte=start_dt)

            if new_member_only:
                items = items.filter(renewal=False)

            if exclude_expired:
                items = items.exclude(status_detail='expired')

            if membership_type:
                items = items.filter(membership_type=membership_type)

            # if order is not specified it sorts by relevance
            if order:
                items = items.order_by(order)

            if items.count() > 0:
                if randomize:
                    if limit:
                        num_to_show = min(items.count(), limit)
                    else:
                        num_to_show = items.count()
                    objects = random.sample(list(items), num_to_show)
                else:
                    objects = items[:limit]

        context[self.context_var] = objects
        return ""


@register.tag
def list_memberships(parser, token):
    """
    Used to pull a list of :model:`memberships.MembershipDefault` items.

    Usage::

        {% list_memberships as [varname] [options] %}

    Be sure the [varname] has a specific name like ``memberships_list``.
    Options can be used as [option]=[value]. Wrap text values
    in quotes like ``limit="6"``. Options include:

        ``limit``
           The number of items that are shown. **Default: 5**
        ``order``
           The order of the items. **Default: Newest Approved**
        ``user``
           Pass in the request.user. **Default: AnonymousUser**
        ``random``
           Use this with a value of true to randomize the items included.
        ``start_dt``
           Specify the date that members joined after this date.
        ``new_member_only``
          Set this to true to exclude renewed ones.
        ``exclude_expired``
          Set this to true to exclude expired ones.

    Example::

        {% list_memberships as membership_list start_dt="6/1/2021" new_member_only=True exclude_expired=True %}
        {% for membership in membership_list %}
            {{ membership.user.first_name }} {{ membership.user.last_name }}
        {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    if len(bits) < 3:
        message = "'%s' tag requires at least 2 parameters" % bits[0]
        raise TemplateSyntaxError(_(message))

    if bits[1] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(_(message))

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = '-join_dt'

    return ListMembershipNode(context_var, *args, **kwargs)
