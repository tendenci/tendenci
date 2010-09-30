from datetime import datetime

from django import template
from django.contrib.auth.models import AnonymousUser
from events.models import Event, Registration

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
    
    def __init__(self, day, type, context_var):

        self.day = template.Variable(day)
        self.type = template.Variable(type)
        self.context_var = context_var
    
    def render(self, context):

        day = self.day.resolve(context)
        type = self.type.resolve(context)

        filters = [
            'start_day:%s' % day.day,
            'start_month:%s' % day.month,
            'start_year:%s' % day.year,
        ]
        if type: filters.append('type:%s' % type)

        sqs = Event.objects.search_filter(filters=filters, user=context['user']).order_by('start_dt')
        events = [sq.object for sq in sqs] 

        context[self.context_var] = events
        return ''

@register.tag
def event_list(parser, token):
    """
    Example: {% event_list day as events %}
             {% event_list day type as events %}
    """
    bits = token.split_contents()
    type = None

    if len(bits) != 4 and len(bits) != 5:
        message = '%s tag requires 4 or 5 arguments' % bits[0]
        raise template.TemplateSyntaxError(message)

    if len(bits) == 4:
        day = bits[1]
        context_var = bits[3]

    if len(bits) == 5:
        day = bits[1]
        type = bits[2]
        context_var = bits[4]
    
    return EventListNode(day, type, context_var)

class IsRegisteredUserNode(template.Node):    
    
    def __init__(self, user, event, context_var):
        self.user = template.Variable(user)
        self.event = template.Variable(event)
        self.context_var = context_var
    
    def render(self, context):

        user = self.user.resolve(context)
        event = self.event.resolve(context)

        if isinstance(user, AnonymousUser):
            exists = False
        else:
            exists = Registration.objects.filter(
                event = event,
                registrant__user=user
            ).exists()

        context[self.context_var] = exists
        return ''

@register.tag
def is_registered_user(parser, token):
    """
    Example: {% is_registered_user user event as registered_user %}
    """
    bits = token.split_contents()

    if len(bits) != 5:
        message = '%s tag requires 5 arguments' % bits[0]
        raise template.TemplateSyntaxError(message)

    user = bits[1]
    event = bits[2]
    context_var = bits[4]

    
    return IsRegisteredUserNode(user, event, context_var)


