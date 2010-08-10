from datetime import datetime
from django import template
from events.models import Event

register = template.Library()

@register.inclusion_tag("events/options.html", takes_context=True)
def event_options(context, user, event):
    context.update({
        "opt_object": event,
        "user": user
    })
    return context

@register.inclusion_tag("events/nav.html", takes_context=True)
def event_nav(context, user, event=None):
    context.update({
        "nav_object" : event,
        "user": user,
        "today": datetime.today()
    })
    return context

@register.inclusion_tag("events/search-form.html", takes_context=True)
def event_search(context):
    return context

@register.inclusion_tag("events/registrants/options.html", takes_context=True)
def registrant_options(context, user, registrant):
    context.update({
        "opt_object": registrant,
        "user": user
    })
    return context

@register.inclusion_tag("events/registrants/search-form.html", takes_context=True)
def registrant_search(context, event=None):

    context.update({
        "event" : event
    })

    return context


class EventListNode(template.Node):    
    
    def __init__(self, day, limit, context_var):
        self.day = template.Variable(day)
        self.limit = template.Variable(limit)
        self.context_var = context_var
    
    def render(self, context):

        day = self.day.resolve(context)
        limit = self.limit.resolve(context)
        kwargs = {
            # i'm being explicit about each date part
            # because I do not want to include the time
            'start_dt__day': day.day,
            'start_dt__month': day.month,
            'start_dt__year': day.year,
        }

        events = Event.objects.filter(**kwargs).order_by('start_dt')

        if limit > 0:
            try: events = events[:limit]
            except: pass

        context[self.context_var] = events
        return ''

@register.tag
def event_list(parser, token):
    """
    Example: {% event_list day as events limit 3 %}
    """
    bits = token.split_contents()
    limit = '0'

    if len(bits) != 4 and len(bits) != 6:
        message = '%s tag requires 4 or 6 arguments' % bits[0]
        raise template.TemplateSyntaxError(message)

    if len(bits) == 4:
        day = bits[1]
        context_var = bits[3]

    if len(bits) == 6:
        limit = bits[5]

    
    return EventListNode(day, limit, context_var)
