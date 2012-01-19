import hashlib
from datetime import datetime, timedelta

from django.contrib.humanize.templatetags.humanize import naturalday
from django.core.urlresolvers import reverse
from django.template.defaultfilters import floatformat
from django.db import models
from django.template import Node, Library, TemplateSyntaxError, Variable
from django.contrib.auth.models import AnonymousUser

from events.models import Event, Registrant, Type, RegConfPricing
from events.utils import get_pricing, registration_earliest_time
from events.utils import registration_has_started, get_event_spots_taken
from events.utils import registration_has_ended
from base.template_tags import ListNode, parse_tag_kwargs

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
        "nav_object": event,
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
        "event": event
    })

    return context


@register.inclusion_tag('events/reg8n/registration_pricing.html', takes_context=True)
def registration_pricing_and_button(context, event, user):
    pricing_context = []
    limit = event.registration_configuration.limit
    spots_taken = 0
    spots_left = limit - spots_taken
    registration = event.registration_configuration

    pricing = RegConfPricing.objects.filter(
        reg_conf=event.registration_configuration,
        status=True,
    )
    reg_started = registration_has_started(event, pricing=pricing)
    reg_ended = registration_has_ended(event, pricing=pricing)
    earliest_time = registration_earliest_time(event, pricing=pricing)

    # dictionary with helpers, not a queryset
    # see get_pricing
    q_pricing = get_pricing(user, event, pricing=pricing)

    # spots taken
    if limit > 0:
        spots_taken = get_event_spots_taken(event)

    is_registrant = False
    # check if user has already registere
    if hasattr(user, 'registrant_set'):
        is_registrant = user.registrant_set.filter(
            registration__event=event).exists()
  
    context.update({
        'now': datetime.now(),
        'event': event,
        'limit': limit,
        'spots_taken': spots_taken,
        'registration': registration,
        'reg_started': reg_started,
        'reg_ended': reg_ended,
        'earliest_time': earliest_time,
        'pricing': q_pricing,
        'user': user,
        'is_registrant': is_registrant,
    })

    return context


class EventListNode(Node):
    def __init__(self, day, type_slug, ordering, context_var):
        #print ordering
        self.day = Variable(day)
        self.type_slug = Variable(type_slug)
        self.ordering = ordering
        if ordering:
            self.ordering = ordering.replace("'",'')
        self.context_var = context_var

    def render(self, context):
        
        day = self.day.resolve(context)
        type_slug = self.type_slug.resolve(context)
        try:
            type = Type.objects.get(slug=type_slug)
        except:
            type = None
        
        day = datetime(day.year, day.month, day.day)
        weekday = day.strftime('%a')
        #one day offset so we can get all the events on that day
        bound = timedelta(hours=23, minutes=59)
        
        sqs = Event.objects.search(date_range=(day+bound, day), user=context['user'])
        
        if type:
            sqs = sqs.filter(type_id=type.pk)
            
        if weekday == 'Sun' or weekday == 'Sat':
            sqs = sqs.filter(on_weekend=True)
        
        if self.ordering:
            sqs = sqs.order_by(self.ordering)
        else:
            sqs = sqs.order_by('number_of_days', 'start_dt')
            
        #print sqs
        events = [sq.object for sq in sqs]
        
        context[self.context_var] = events
        return ''


@register.tag
def event_list(parser, token):
    """
    Example: {% event_list day as events %}
             {% event_list day type as events %}
             {% event_list day type 'start_dt' as events %}
    """
    bits = token.split_contents()
    type_slug = None
    ordering = None

    if len(bits) != 4 and len(bits) != 5 and len(bits) != 6:
        message = '%s tag requires 4 or 5 or 6 arguments' % bits[0]
        raise TemplateSyntaxError(message)

    if len(bits) == 4:
        day = bits[1]
        context_var = bits[3]

    if len(bits) == 5:
        day = bits[1]
        type_slug = bits[2]
        context_var = bits[4]
        
    if len(bits) == 6:
        day = bits[1]
        type_slug = bits[2]
        ordering = bits[3]
        context_var = bits[5]

    return EventListNode(day, type_slug, ordering, context_var)


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
                registration__event=event,
                email=user.email,
                cancel_dt=None,
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


class ListEventsNode(ListNode):
    model = Event
    
    def __init__(self, context_var, *args, **kwargs):
        self.context_var = context_var
        self.kwargs = kwargs

        if not self.model:
            raise AttributeError(_('Model attribute must be set'))
        if not issubclass(self.model, models.Model):
            raise AttributeError(_('Model attribute must derive from Model'))
        if not hasattr(self.model.objects, 'search'):
            raise AttributeError(_('Model.objects does not have a search method'))

    def render(self, context):
        tags = u''
        query = u''
        user = AnonymousUser()
        limit = 3
        order = 'next_upcoming'

        randomize = False

        if 'random' in self.kwargs:
            randomize = bool(self.kwargs['random'])

        if 'tags' in self.kwargs:
            try:
                tags = Variable(self.kwargs['tags'])
                tags = unicode(tags.resolve(context))
            except:
                tags = self.kwargs['tags']

            tags = tags.replace('"', '')
            tags = tags.split(',')

        if 'user' in self.kwargs:
            try:
                user = Variable(self.kwargs['user'])
                user = user.resolve(context)
            except:
                user = self.kwargs['user']
        else:
            # check the context for an already existing user
            if 'user' in context:
                user = context['user']

        if 'limit' in self.kwargs:
            try:
                limit = Variable(self.kwargs['limit'])
                limit = limit.resolve(context)
            except:
                limit = self.kwargs['limit']

        limit = int(limit)

        if 'query' in self.kwargs:
            try:
                query = Variable(self.kwargs['query'])
                query = query.resolve(context)
            except:
                query = self.kwargs['query']  # context string

        if 'order' in self.kwargs:
            try:
                order = Variable(self.kwargs['order'])
                order = order.resolve(context)
            except:
                order = self.kwargs['order']

        # process tags
        for tag in tags:
            tag = tag.strip()
            query = '%s "tag:%s"' % (query, tag)

        # get the list of staff
        items = self.model.objects.search(user=user, query=query)
        objects = []
        # if order is not specified it sorts by relevance

        if order:
            if order == "next_upcoming":
                items = items.filter(start_dt__gt = datetime.now())
                items = items.order_by("start_dt")
            else:
                items = items.order_by(order)

        if items:
            if randomize:
                objects = [item.object for item in random.sample(items, items.count())][:limit]
            else:
                objects = [item.object for item in items[:limit]]

        context[self.context_var] = objects
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

    if len(bits) < 3:
        message = "'%s' tag requires more than 3" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "as":
        message = "'%s' second argument must be 'as" % bits[0]
        raise TemplateSyntaxError(message)

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = 'next_upcoming'

    return ListEventsNode(context_var, *args, **kwargs)

