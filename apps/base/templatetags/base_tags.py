from django.template import Library, Node, Variable, TemplateSyntaxError
from django.core.urlresolvers import reverse

from base.utils import url_exists

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