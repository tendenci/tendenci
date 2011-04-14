from django.template import Node, Library, TemplateSyntaxError, Variable
from django.template.loader import get_template
from django.utils.safestring import mark_safe

from base.template_tags import ListNode, parse_tag_kwargs
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
            output = '<div id="box-%s" class="boxes">%s %s</div>' % (
                box.object.pk,
                box.object.content,
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
    Example:

    {% list_boxes as boxes [user=user limit=3 tags=bloop bleep q=searchterm pk=123] %}
    {% for box in boxes %}
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
