from django.template import Library, Node, Variable, TemplateSyntaxError
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from base.utils import url_exists

from profiles.models import Profile

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
        if self.object:
            object = self.object.resolve(context)
            has_perm = user.has_perm(self.perm, object)
        else:
            has_perm = user.has_perm(self.perm)
            
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
    bits  = token.split_contents()
    
    try: user = bits[1]
    except: user = None
    
    try: perm = bits[2]
    except: perm = None
        
    try: object = bits[3]
    except: object = None
    
    if object == 'as':
        object = None
        try: context_var = bits[4]
        except: context_var = None
    else:
        try: context_var = bits[5]
        except: context_var = None
    
    return HasPermNode(user, perm, object, context_var=context_var)


def callMethod(obj, methodName):
    """
        callMethod and args are used so that we can call a method with parameters in template
        Example:
            if you want to call: user_this.allow_view_by(user_current)
            in template: {{ user_this.get_profile|args:user_current|call:'allow_edit_by' }}
    """
    method = getattr(obj, methodName)
 
    if obj.__dict__.has_key("__callArg"):
        ret = method(*obj.__callArg)
        del obj.__callArg
        return ret
    return method()
 
def args(obj, arg):
    if not obj.__dict__.has_key("__callArg"):
        obj.__callArg = []
     
    obj.__callArg += [arg]
    return obj
 
register.filter("call", callMethod)
register.filter("args", args)


# so we can create new variables in template
# {% assign [name] [value] %}
class AssignNode(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value
        
    def render(self, context):
        context[self.name] = self.value.resolve(context, True)
        return ''

def do_assign(parser, token):
    """
    Assign an expression to a variable in the current context.
    
    Syntax::
        {% assign [name] [value] %}
    Example::
        {% assign list entry.get_related %}
        
    """
    bits = token.contents.split()
    if len(bits) != 3:
        raise TemplateSyntaxError("'%s' tag takes two arguments" % bits[0])
    value = parser.compile_filter(bits[2])
    return AssignNode(bits[1], value)

register.tag('assign', do_assign)


class GetProfileNode(Node):
    def __init__(self, obj, var_name):
        self.user_obj = obj
        self.var_name = var_name
        
    def resolve(self, var, context):
        """Resolves a variable out of context if it's not in quotes"""
        if var[0] in ('"', "'") and var[-1] == var[0]:
            return var[1:-1]
        else:
            return Variable(var).resolve(context)
        
    def render(self, context):
        user_obj = self.resolve(self.user_obj, context)
        var_name = self.resolve(self.var_name, context)
        if isinstance(user_obj, User):
            try:
                profile = user_obj.get_profile()
            except Profile.DoesNotExist:
                profile = Profile.objects.create_profile(user=user_obj)
    
        context[var_name] = profile
        return ""

def get_or_create_profile_for(parser, token):
    """
    Get or create a user profile if not exists
    
    Example::
        {% get_or_create_profile user_this %}
        
    """
    bits = token.contents.split()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' tag takes at least two arguments" % bits[0])
    
    args = {
        'obj': bits[1],
        'var_name': next_bit_for(bits, 'as'),
    }
    return GetProfileNode(**args)

def next_bit_for(bits, key, if_none=None, step=1):
    try:
        return bits[bits.index(key)+step]
    except ValueError:
        return if_none

register.tag('get_or_create_profile_for', get_or_create_profile_for)

class ResetNode(Node):
    def __init__(self, variable, **kwargs):
        # set the context var
        self.variable = Variable(variable)
            
        # get the context vars
        for k, v in kwargs.items():
            if k == 'context':
                self.context = v
            
    def render(self, context):
        variable = self.variable.resolve(context)
        context[self.context] = variable 
        return ''

@register.tag      
def reset(parser, token):
    """
        Reset a context variable to another one
        {% reset var as var1 %} 
    """
    bits = token.split_contents()

    try:
        variable = bits[1]
    except:
        raise TemplateSyntaxError, "'%s' requires at least three arguments." % bits[0]
    
    if bits[1] == 'as':
        raise TemplateSyntaxError, "'%s' first argument must be a context var." % bits[0]
    
    # get the user
    try:
        variable = bits[bits.index('as')-1]
        context = bits[bits.index('as')+1]
    except:
        variable = None
        context = None
    
    if not variable and not context:
        raise TemplateSyntaxError, "'%s' missing arguments. Syntax {% reset var1 as var2 %}" % bits[0]
    
    return ResetNode(variable, context=context)

class ImagePreviewNode(Node):
    def __init__(self, instance, size, **kwargs):
        # set the context var
        self.instance = Variable(instance)    
        self.size = size
        self.context = None
        
        # get the context vars
        for k, v in kwargs.items():
            if k == 'context':
                self.context = v
            
    def render(self, context):
        instance = self.instance.resolve(context)
        
        app_label = instance._meta.app_label
        model = instance._meta.object_name.lower()
        
        url = reverse('image_preview', args=(app_label, model, instance.id, self.size))
        if not url_exists(url):
            url = None
              
        if self.context:
            context[self.context] = url 
        else:
            context['image_preview'] = url
        
        return ''

@register.tag      
def image_preview(parser, token):
    """
        Gets the url for an image preview base
        on model and model_id
    """
    bits = token.split_contents()
    
    try:
        instance = bits[1]
    except:
        raise TemplateSyntaxError, "'%s' requires at least 2 arguments" % bits[0]
        
    try:
        size = bits[2]
    except:
        raise TemplateSyntaxError, "'%s' requires at least 2 arguments" % bits[0]        
         
    try:
        context = bits[4]
    except:
        context = "image_preview"
        
    return ImagePreviewNode(instance, size, context=context)

