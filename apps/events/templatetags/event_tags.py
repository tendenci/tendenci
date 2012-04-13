import hashlib
from datetime import datetime, timedelta
from operator import or_

from django.contrib.humanize.templatetags.humanize import naturalday
from django.core.urlresolvers import reverse
from django.template.defaultfilters import floatformat
from django.db import models
from django.template import Node, Library, TemplateSyntaxError, Variable
from django.contrib.auth.models import AnonymousUser, User
from django.db.models import Q

from base.template_tags import ListNode, parse_tag_kwargs
from site_settings.utils import get_setting
from perms.utils import get_query_filters

from events.models import Event, Registrant, Type, RegConfPricing
from events.utils import get_pricing, registration_earliest_time
from events.utils import registration_has_started, get_event_spots_taken
from events.utils import registration_has_ended

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
    
    # setting for allowing anonymous members to choose prices
    anonpricing = get_setting('module', 'events', 'anonymousmemberpricing')
    
    # dictionary with helpers, not a queryset
    # see get_pricing
    q_pricing = get_pricing(user, event, pricing=pricing)
    
    # spots taken
    if limit > 0:
        spots_taken = get_event_spots_taken(event)
    
    is_registrant = False
    # check if user has already registered
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
        'anonpricing': anonpricing,
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

        types = Type.objects.filter(slug=type_slug)

        type = None
        if types:
            type = types[0]

        day = datetime(day.year, day.month, day.day)
        weekday = day.strftime('%a')

        #one day offset so we can get all the events on that day
        bound = timedelta(hours=23, minutes=59)

        start_dt = day+bound
        end_dt = day

        filters = get_query_filters(context['user'], 'events.view_event')
        events = Event.objects.filter(filters).filter(start_dt__lte=start_dt, end_dt__gte=end_dt).distinct()

        if type:
            events = events.filter(type=type)

        if weekday == 'Sun' or weekday == 'Sat':
            events = events.filter(on_weekend=True)

        events = events.order_by(self.ordering or 'start_dt')
        
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
        event_type = ''

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
                if user == "anon" or user == "anonymous":
                    user = AnonymousUser()
        else:
            # check the context for an already existing user
            # and see if it is really a user object
            if 'user' in context:
                if isinstance(context['user'], User):
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

        if 'type' in self.kwargs:
            try:
                event_type = Variable(self.kwargs['type'])
                event_type = event_type.resolve(context)
            except:
                event_type = self.kwargs['type']

        filters = get_query_filters(user, 'events.view_event')
        items = Event.objects.filter(filters).distinct()
        if event_type:
            items = items.filter(type__name__iexact=event_type)

        if tags:  # tags is a comma delimited list
            # this is fast; but has one hole
            # it finds words inside of other words
            # e.g. "event" is within "prevent"
            tag_queries = [Q(tags__icontains=t) for t in tags]
            tag_query = reduce(or_, tag_queries)
            items = items.filter(tag_query)

        objects = []

        # if order is not specified it sorts by relevance
        if order:
            if order == "next_upcoming":
                # Removed seconds so we can cache the query better
                now = datetime.now().replace(second=0)
                items = items.filter(start_dt__gt = now)
                items = items.order_by("start_dt")
            else:
                items = items.order_by(order)

        if items:
            if randomize:
                objects = [item for item in random.sample(items, items.count())][:limit]
            else:
                objects = [item for item in items[:limit]]

        context[self.context_var] = objects
        return ""


@register.tag
def list_events(parser, token):
    """
    Used to pull a list of :model:`events.Event` items.

    Usage::

        {% list_events as [varname] [options] %}

    Be sure the [varname] has a specific name like ``events_sidebar`` or 
    ``events_list``. Options can be used as [option]=[value]. Wrap text values
    in quotes like ``tags="cool"``. Options include:
    
        ``limit``
           The number of items that are shown. **Default: 3**
        ``order``
           The order of the items. **Default: Next Upcoming by date**
        ``user``
           Specify a user to only show public items to all. **Default: Viewing user**
        ``type``
           The type of the event.
        ``tags``
           The tags required on items to be included.
        ``random``
           Use this with a value of true to randomize the items included.

    Example::

        {% list_events as events_list limit=5 tags="cool" %}
        {% for event in events_list %}
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

