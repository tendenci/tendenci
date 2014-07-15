from django.template import Library, Node, Variable
from django.contrib.auth.models import User

from tendenci.core.perms import utils
from tendenci.core.perms.fields import groups_with_perms

register = Library()


class HasPermNode(Node):
    def __init__(self, user, perm, object=None, context_var=None):
        self.perm = perm
        self.context_var = context_var
        self.user = Variable(user)
        if object:
            self.object = Variable(object)
        else:
            self.object = object

    def render(self, context):
        if not self.user and not self.perm:
            return False

        has_perm = False
        user = self.user.resolve(context)

        if isinstance(user, User):

            # return true for admins
            if user.profile.is_superuser:
                has_perm = True
            else:
                if self.object:
                    object = self.object.resolve(context)
                    has_perm = utils.has_perm(user, self.perm, object)
                else:
                    has_perm = utils.has_perm(user, self.perm)

        if self.context_var:
            context[self.context_var] = has_perm
            return ''
        else:
            return has_perm


@register.tag
def has_perm(parser, token):
    """
        {% has_perm user perm instance as context}
        {% has_perm user perm as context}
    """
    bits = token.split_contents()

    try:
        user = bits[1]
    except:
        user = None

    try:
        perm = bits[2]
    except:
        perm = None

    try:
        object = bits[3]
    except:
        object = None

    if object == 'as':
        object = None
        try:
            context_var = bits[4]
        except:
            context_var = None
    else:
        try: context_var = bits[5]
        except: context_var = None

    return HasPermNode(user, perm, object, context_var=context_var)


class IsAdminNode(Node):
    def __init__(self, user, context_var):
        self.user = user
        self.var_name = context_var

    def resolve(self, var, context):
        if 'request' in context or 'user' in context:
            return Variable(var).resolve(context)
        return None

    def render(self, context):
        user = self.resolve(self.user, context)

        if isinstance(user, User):
            is_superuser = user.profile.is_superuser
        else:
            is_superuser = False

        if self.var_name:
            context[self.var_name] = is_superuser
            return ""
        else:
            return is_superuser


@register.tag
def is_admin(parser, token):
    """
        {% is_admin user as context %}
        This has been deprecated in favor of request.user.is_superuser
    """
#     import warnings
#     warnings.warn('stop using is_admin, please use user.is_superuser', DeprecationWarning)

    bits = token.split_contents()

    try:
        user = bits[1]
    except:
        user = None

    if len(bits) >= 4:
        context_var = bits[3]
    else:
        context_var = None
    return IsAdminNode(user, context_var=context_var)


class IsDeveloperNode(Node):
    def __init__(self, user, context_var):
        self.user = user
        self.var_name = context_var

    def resolve(self, var, context):
        return Variable(var).resolve(context)

    def render(self, context):
        user = self.resolve(self.user, context)

        if isinstance(user, User):
            is_superuser = user.profile.is_superuser
        else:
            is_superuser = False

        if self.var_name:
            context[self.var_name] = is_superuser
            return ""
        else:
            return is_superuser

@register.tag
def is_developer(parser, token):
    """
        {% is_developer user as context %}

        This has been deprecated in favor of request.user.is_superuser
    """
    bits  = token.split_contents()

    try: user = bits[1]
    except: user = None

    if len(bits) >= 4:
        context_var = bits[3]
    else:
        context_var = None
    return IsDeveloperNode(user, context_var=context_var)

@register.simple_tag
def obj_perms(obj):

    t = '<span class="perm-%s">%s</span>'

    if obj.allow_anonymous_view:
        value = t % ('public','Public')
    elif obj.allow_user_view:
        value = t % ('users','Users')
    elif obj.allow_member_view:
        value = t % ('members','Members')
    elif groups_with_perms(obj):
        value = t % ('groups','Groups')
    else:
        value = t % ('private','Private')

    return value

@register.simple_tag
def obj_status(obj):
    t = '<span class="status-%s">%s</span>'

    if obj.status:
        value = t % (obj.status_detail, obj.status_detail.capitalize())
    else:
        value = t % ('inactive','Inactive')

    return value

