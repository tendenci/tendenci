from django.template import Node, Library, TemplateSyntaxError, Variable
from quotes.models import Quote

register = Library()

class ListQuotesNode(Node):
    def __init__(self, context_var, *args, **kwargs):
        self.context_var = context_var
        self.kwargs = kwargs

    def render(self, context):

        limit = 3
        user = None
        tags = ''
        query = ''

        if 'limit' in self.kwargs:
            try:
                limit = Variable(self.kwargs['limit'])
                limit = limit.resolve(context)
            except:
                pass # use default

        if 'user' in self.kwargs:
            try:
                user = Variable(self.kwargs['user'])
                user = user.resolve(context)
            except:
                pass # use default
        else:
            # check the context for an already existing user
            if 'user' in context:
                user = context['user']

        if 'tags' in self.kwargs:
            try:
                tags = Variable(self.kwargs['tags'])
                tags = unicode(tags.resolve(context))
            except:
                tags = self.kwargs['tags'] # context string
            tags = tags.split(',')

        q = self.kwargs.get('q') or []

        for tag in tags:
            query = '%s "tag:%s"' % (query, tag.strip())

        for q_item in q:
            query = '%s "%s"' % (query, q_item.strip())

        quotes = Quote.objects.search(user=user, query=query)
        quotes = quotes.order_by('create_dt')
        context[self.context_var] = [quote.object for quote in quotes[:limit]]

        return ''

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

