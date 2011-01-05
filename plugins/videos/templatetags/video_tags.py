from django.template import Node, Library, TemplateSyntaxError, Variable
from videos.models import Video

register = Library()

class ListVideosNode(Node):
    
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

        self.tags = self.tags.resolve(context)
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


        videos = Video.objects.search(user=self.user, query=query)
        videos = videos.order_by('create_dt')
        videos = [video.object for video in videos[:self.limit]]
        context[self.context_var] = videos
        return ""

@register.tag
def list_videos(parser, token):
    """
    Example:
        {% list_videos as videos [user=user limit=3 tags=bloop bleep q=searchterm] %}
        {% for video in videos %}
            {{ video.title }}
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

    return ListVideosNode(context_var, *args, **kwargs)

