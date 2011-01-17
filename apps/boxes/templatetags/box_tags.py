from django.template import Node, Library, TemplateSyntaxError, Variable
from django.template.loader import get_template
from django.utils.safestring import mark_safe

from boxes.models import Box

register = Library()


class GetBoxNode(Node):
    
    def __init__(self, pk):
        self.pk = pk

    def render(self, context):
        query = '"pk:%s"' % (self.pk)
        try:
            box = Box.objects.search(query=query).best_match()
            context['box'] = box.object
            template = get_template('boxes/edit-link.html')
            output = '<div class="boxes">%s %s</div>' % (box.object.content, template.render(context),)
            return output
        except:
            return ""
        
@register.tag
def box(parser, token):
    """
    Example:
        {% box 123 %}
    """
    bits = token.split_contents()
    
    try:
        pk = bits[1]  
    except:
        message = "Box tag must include an ID of a box."
        raise TemplateSyntaxError(message)
    
    return GetBoxNode(pk)  

# Output the box as safe HTML
box.safe = True 
    
       

class ListBoxesNode(Node):
    
    def __init__(self, context_var, *args, **kwargs):

        self.limit = 3
        self.user = None
        self.tags = ''
        self.q = []
        self.pk = ''
        self.context_var = context_var

        if "limit" in kwargs:
            self.limit = Variable(kwargs["limit"])
        if "user" in kwargs:
            self.user = Variable(kwargs["user"])
        if "tags" in kwargs:
            self.tags_string = kwargs['tags']
            self.tags = Variable(kwargs["tags"])
        if "q" in kwargs:
            self.q = kwargs["q"]
        if "pk" in kwargs:
            self.pk = kwargs["pk"]

    def render(self, context):
        query = ''

        try:
            self.tags = self.tags.resolve(context)
        except:
            self.tags = self.tags_string
        
        if self.tags:
            self.tags = self.tags.split(',')
        if not self.tags:
            self.tags = self.tags_string.split(',')
        
        if self.user:
            self.user = self.user.resolve(context)

        if hasattr(self.limit, "resolve"):
            self.limit = self.limit.resolve(context)

        for tag in self.tags:
            tag = tag.strip()
            query = '%s "tag:%s"' % (query, tag)
                    
        for q_item in self.q:
            q_item = q_item.strip()
            query = '%s "%s"' % (query, q_item)
            
        if self.pk:
            query = '%s "pk:%s"' % (query, self.pk)
        
        boxes = Box.objects.search(user=self.user, query=query)
        boxes = boxes.order_by('create_dt')
        boxes = [box.object for box in boxes[:self.limit]]
        
        context[self.context_var] = boxes
        return ""

@register.tag
def list_boxes(parser, token):
    """
    Example:
        {% list_boxes as boxes [user=user limit=3 tags=bloop bleep q=searchterm pk=123] %}
        {% for box in boxes %}
            <div class="boxes">{{ box.get_content }}</div>
        {% endfor %}

    """
    args, kwargs = [], {}
    bits = token.split_contents()
    
    if len(bits) < 3:
        message = "'%s' tag requires more than 2" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(message)
        
    context_var = bits[2]

    for bit in bits:
        if "limit=" in bit:
            kwargs["limit"] = bit.split("=")[1]
        if "user=" in bit:
            kwargs["user"] = bit.split("=")[1]
        if "tags=" in bit:
            kwargs["tags"] = bit.split("=")[1].replace('"','')
        if "q=" in bit:
            kwargs["q"] = bit.split("=")[1].replace('"','').split(',')
        if "pk=" in bit:
            kwargs["pk"] = bit.split("=")[1]

   

    return ListBoxesNode(context_var, *args, **kwargs)

