import re

from django.template import RequestContext, Context, Template

def detect_template_tags(string):
    """
        Used to detect wether or not any string contains
        template tags in the system
        returns boolean
    """
    import re
    p = re.compile('{[#{%][^#}%]+[%}#]}', re.IGNORECASE)
    return p.search(string)

def render_content(content, arg=None, limit=None, image_preview=True):
    """
        checks for template tags within the content and rendered them
        currently it is only rendering streams
    """
    match = detect_template_tags(content)

    if match:
        p = re.compile('{%([\w\s\=]+)%}')
        tags = list(set(re.findall(p, content)))
        TEMPLATE_TAGS = ['{% load box_tags %}']
        if tags:
            for tag in tags:
                tag = "{%"+tag+"%}"
                context = Context({'user':None})
                t = Template(''.join(TEMPLATE_TAGS) + tag)
                rendered_tag = t.render(context)
                content = content.replace(tag, rendered_tag)
    return content
