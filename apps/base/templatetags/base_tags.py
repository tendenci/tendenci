from django.template import Library, Node, Variable, TemplateSyntaxError 

register = Library()

class HasPermNode(Node):
    def __init__(self, user, perm, object=None, context_var=None):
        self.user = Variable(user)
        self.perm = perm
        self.object = Variable(object)
        self.context_var = context_var
        
    def render(self, context):
        if not self.user and not self.perm:
            return False
        
        user = self.user.resolve(context)
        object = self.object.resolve(context)
        
        if self.context_var:
            context[self.context_var] = user.has_perm(self.perm, object)
            return ''
        else:
            return user.has_perm(self.perm, object)

@register.tag
def has_perm(parser, token):
    """
        {% has_perm user, perm, article}
    """
    bits  = token.split_contents()
    
    try: user = bits[1]
    except: user = None
    
    try: perm = bits[2]
    except: perm = None
        
    try: object = bits[3]
    except: object = None
    
    try: context_var = bits[5]
    except: context_var = None
               
    return HasPermNode(user, perm, object, context_var=context_var)