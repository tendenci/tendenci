from django.template import Library, Node, Variable, TemplateSyntaxError 

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