from django.template import Node, Library, TemplateSyntaxError, Variable
from quotes.models import Quote

register = Library()

class ListQuotesNode(Node):
    
    def __init__(self, context_var, *args, **kwargs):

        self.limit = 3
        self.user = None
        self.tags = ''
        self.q = []
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


        quotes = Quote.objects.search(user=self.user, query=query)
        quotes = quotes.order_by('create_dt')
        quotes = [quote.object for quote in quotes[:self.limit]]
        context[self.context_var] = quotes
        return ""

@register.tag
def list_quotes(parser, token):
    """
    Example:
        {% list_quotes as quotes_list [user=user limit=3 tags=bloop bleep q=searchterm] %}
        {% for quote in quotes %}
            {{ quote.quote }}
        {% endfor %}

    """
    args, kwargs = [], {}
    bits = token.split_contents()
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

    if len(bits) < 3:
        message = "'%s' tag requires more than 2" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(message)

    return ListQuotesNode(context_var, *args, **kwargs)

