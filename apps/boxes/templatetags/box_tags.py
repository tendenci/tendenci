from django.template import Node, Library, TemplateSyntaxError, Variable
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.contrib.auth.models import AnonymousUser, User

from perms.utils import get_query_filters
from base.template_tags import ListNode, parse_tag_kwargs
from boxes.models import Box

register = Library()


class GetBoxNode(Node):
    def __init__(self, pk):
        self.pk = pk

    def render(self, context):
        query = '"pk:%s"' % (self.pk)
        user = AnonymousUser()
        
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
        try:
            filters = get_query_filters(user, 'boxes.view_box')
            box = Box.objects.filter(filters).filter(pk=self.pk).distinct()
            context['box'] = box[0]
            template = get_template('boxes/edit-link.html')
            output = '<div id="box-%s" class="boxes">%s %s</div>' % (
                box[0].pk,
                box[0].content,
                template.render(context),
            )
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


class ListBoxesNode(ListNode):
    model = Box


@register.tag
def list_boxes(parser, token):
    """
    Used to pull a list of :model:`boxes.Box` items.

    Usage::

        {% list_boxes as [varname] [options] %}

    Be sure the [varname] has a specific name like ``boxes_sidebar`` or 
    ``boxes_list``. Options can be used as [option]=[value]. Wrap text values
    in quotes like ``tags="cool"``. Options include:
    
        ``limit``
           The number of items that are shown. **Default: 3**
        ``order``
           The order of the items. **Default: Newest First**
        ``user``
           Specify a user to only show public items to all. **Default: Viewing user**
        ``query``
           The text to search for items. Will not affect order.
        ``tags``
           The tags required on items to be included.
        ``random``
           Use this with a value of true to randomize the items included.

    Example::

        {% list_boxes as boxes_list limit=5 tags="cool" %}
        {% for box in boxes_list %}
            <div class="boxes">{{ box.safe_content }}
            {% include 'boxes/edit-link.html' %}</div>
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

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = '-create_dt'

    return ListBoxesNode(context_var, *args, **kwargs)
