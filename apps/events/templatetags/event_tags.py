import hashlib
from datetime import datetime
from django.contrib.humanize.templatetags.humanize import naturalday
from django.core.urlresolvers import reverse

from django.template import Node, Library, TemplateSyntaxError, Variable
from django.contrib.auth.models import AnonymousUser
from events.models import Event, Registrant, Type
from django.template.defaultfilters import floatformat


register = Library()

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

@register.inclusion_tag('events/reg8n/register-button.html', takes_context=True)
def register_button(context):
    event = context['event']
    user = context['user']
    reg8n_config = event.registration_configuration

    # Set the variables ------------------

    reg8n_enabled = reg8n_config and reg8n_config.enabled

    if reg8n_enabled:
        reg8n_price = reg8n_config.price or float(0)

    if user.is_anonymous():
        registrant = False
    else:
        registrant = Registrant.objects.filter(
            registration__event = event,
            email = user.email,
            cancel_dt = None,
        ).exists()

    registrants = Registrant.objects.filter(registration__event=event)
    if reg8n_config.payment_required:
        registrants = registrants.filter(registration__invoice__balance__lte=0)

    reg8n_full = registrants.count() >= reg8n_config.limit

    ## Do the logic ----------------------

    url1,msg1,msg2,status_class = '','','',''

    if reg8n_enabled:
        if reg8n_config.within_time:

            msg2 = 'Registration ends %s' % naturalday(reg8n_config.late_dt)
            status_class = 'open'
            url1 = reverse('event.register', args=[event.pk])

            if registrant:
                msg1 = 'You are registered'
                status_class = 'registered'
                url1 = registrant.hash_url
            else:

                if reg8n_price:
                    msg1 = '$%s to Register' % floatformat(reg8n_price)
                else:
                    msg1 = 'Register for Free'

                if reg8n_full:
                    msg1 = 'Registration Full'
                    status_class = 'closed'
                    url1 = ''
        else:

            if reg8n_config.early_dt > datetime.now():
                msg2 = 'Registration opens %s' % naturalday(reg8n_config.early_dt)
            else:
                msg2 = 'Registration ended %s' % naturalday(reg8n_config.late_dt)

            status_class = 'closed'

            if registrant:
                msg1 = 'You are registered'
                status_class = 'registered'
                url1 = registrant.hash_url
            else:
                msg1 = 'Registration Closed'

    return {'reg8n_enabled':reg8n_enabled, 'url1':url1, 'msg1':msg1, 'msg2':msg2, 'status_class':status_class}

class EventListNode(Node):    
    
    def __init__(self, day, type_slug, context_var):

        self.day = Variable(day)
        self.type_slug = Variable(type_slug)
        self.context_var = context_var
    
    def render(self, context):

        day = self.day.resolve(context)
        type_slug = self.type_slug.resolve(context)
        type = None

        filters = [
            'start_day:%s' % day.day,
            'start_month:%s' % day.month,
            'start_year:%s' % day.year,
        ]

        type_sqs = Type.objects.search()
        type_sqs = type_sqs.filter(slug=type_slug)

        if type_sqs and type_sqs[0]:
            type = type_sqs[0].object
          
        if type: filters.append('type_id:%s' % type.pk)

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
    type_slug = None

    if len(bits) != 4 and len(bits) != 5:
        message = '%s tag requires 4 or 5 arguments' % bits[0]
        raise TemplateSyntaxError(message)

    if len(bits) == 4:
        day = bits[1]
        context_var = bits[3]

    if len(bits) == 5:
        day = bits[1]
        type_slug = bits[2]
        context_var = bits[4]
    
    return EventListNode(day, type_slug, context_var)

class IsRegisteredUserNode(Node):    
    
    def __init__(self, user, event, context_var):
        self.user = Variable(user)
        self.event = Variable(event)
        self.context_var = context_var
    
    def render(self, context):

        user = self.user.resolve(context)
        event = self.event.resolve(context)

        if isinstance(user, AnonymousUser):
            exists = False
        else:
            exists = Registrant.objects.filter(
                registration__event = event,
                email = user.email,
                cancel_dt = None,
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
        raise TemplateSyntaxError(message)

    user = bits[1]
    event = bits[2]
    context_var = bits[4]

    
    return IsRegisteredUserNode(user, event, context_var)


class ListEventsNode(Node):
    
    def __init__(self, context_var, *args, **kwargs):

        self.limit = 3
        self.user = None
        self.tags = []
        self.q = []
        self.context_var = context_var

        if "limit" in kwargs:
            self.limit = Variable(kwargs["limit"])
        if "user" in kwargs:
            self.user = Variable(kwargs["user"])
        if "tags" in kwargs:
            self.tags = kwargs["tags"]
        if "q" in kwargs:
            self.q = kwargs["q"]

    def render(self, context):
        query = ''

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

        events = Event.objects.search(user=self.user, query=query)

        events = [event.object for event in events[:self.limit]]
        context[self.context_var] = events
        return ""

@register.tag
def list_events(parser, token):
    """
    Example:
        {% list_events as events [user=user limit=3] %}
        {% for event in events %}
            {{ event.title }}
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
            kwargs["tags"] = bit.split("=")[1].replace('"','').split(',')
        if "q=" in bit:
            kwargs["q"] = bit.split("=")[1].replace('"','').split(',')

    if len(bits) < 3:
        message = "'%s' tag requires more than 3" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "as":
        message = "'%s' second argument must be 'as" % bits[0]
        raise TemplateSyntaxError(message)

    return ListEventsNode(context_var, *args, **kwargs)


