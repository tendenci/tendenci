from time import strptime
from datetime import datetime, timedelta
from operator import and_

from socket import gethostbyname, gethostname
from django.db.models import Manager
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.conf import settings

from robots.models import Robot

from haystack.query import SearchQuerySet

default_keyword_args = (
    'request',
    'user',
    'instance',
    'category',
    'event_id',
    'event_name',
    'event_type',
    'event_data',
    'description',
    'entity',
    'source',
)


class EventLogManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
        Uses haystack to query event logs
        Returns a SearchQuerySet
        """
        f_data = query.cleaned_data
        qs = []

        if f_data['start_dt']:
            qs.append(Q(create_dt__gte=f_data['start_dt']))
        else:
            qs.append(Q(create_dt__gte=datetime.now() - timedelta(weeks=4)))

        if f_data['end_dt']:
            qs.append(Q(create_dt__lte=f_data['end_dt']))
        else:
            qs.append(Q(create_dt__lte=datetime.now()))

        if f_data['request_method']:
            if f_data['request_method'] != 'all':
                qs.append(Q(request_method=f_data['request_method']))

        if f_data['event_id']:
            qs.append(Q(event_id=f_data['event_id']))

        if f_data['user_id']:
            qs.append(Q(user=f_data['user_id']))

        if f_data['user_name']:
            qs.append(Q(username=f_data['user_name']))

        if f_data['user_ip_address']:
            qs.append(Q(user_ip_address=f_data['user_ip_address']))

        if f_data['session_id']:
            qs.append(Q(session_id=f_data['session_id']))

        if f_data['source']:
            qs.append(Q(source=f_data['source']))

        event_logs = self.model.objects.filter(
            reduce(and_, qs)
        )

        return event_logs.order_by('-create_dt')

    def log(self, **kwargs):
        """
        EventLog.objects.log(**kwargs)
        Optional Keyword Arguments:
            request - request object from a view
            user - any user instance
            instance - any model instance
            category - defaults to 'application'
            event_name - default to 'application'
            event_type - defaults to 'information'
            source - defaults to app_label if instance is passed
            entity - entity object
        Required keyword Arguments:
            event_id
            event_data
            description

        Simple Example:
        from event_logs.utils import log_event
        event_log_defaults = {
            'event_id': 123000,
            'event_data': 'added by glenbot'
            'description': 'article added'
        }
        EventLog.objects.log(**eventlog_defaults)
        """
        request, user, instance = None, None, None
        event_log = self.model()

        if not kwargs:
            raise TypeError('At least event_id, event_data, description keyword arguments are expected')

        for kwarg in kwargs:
            if kwarg not in default_keyword_args:
                raise TypeError('Unexpected keyword argument %s' % kwarg)

        # check the required arguments
        if 'event_id' in kwargs:
            event_log.event_id = kwargs['event_id']
        else:
            raise TypeError('Keyword argument event_id is required')

        if 'event_data' in kwargs:
            event_log.event_data = kwargs['event_data']
        else:
            raise TypeError('Keyword argument event_data is required')

        if 'description' in kwargs:
            event_log.description = kwargs['description']
        else:
            raise TypeError('Keyword argument description is required')

        # object parameters
        if 'request' in kwargs:
            request = kwargs['request']

        if 'user' in kwargs:
            user = kwargs['user']

        if 'instance' in kwargs:
            instance = kwargs['instance']

        # non object parameters
        if 'category' in kwargs:
            event_log.category = kwargs['category']
        if 'event_name' in kwargs:
            event_log.event_name = kwargs['event_name']
        if 'event_type' in kwargs:
            event_log.event_type = kwargs['event_type']
        if 'source' in kwargs:
            event_log.source = kwargs['source']

        event_log.entity = None
        if 'entity' in kwargs:
            event_log.entity = kwargs['entity']

        if not event_log.category:
            event_log.category = 'application'
        if not event_log.event_name:
            event_log.event_name = 'application'
        if not event_log.event_type:
            event_log.event_type = 'information'

        # set up the user information
        if user:
            # check for impersonation and set the correct user, descriptions, etc
            impersonated_user = getattr(user, 'impersonated_user', None)
            if impersonated_user:
                event_log.event_data = '%s (impersonating %s)' % (
                    event_log.event_data,
                    impersonated_user.username,
                )

            if isinstance(user, AnonymousUser):
                event_log.username = 'anonymous'
            else:
                event_log.user = user
                event_log.username = user.username
                event_log.email = user.email

        # setup request meta information
        if request:
            if hasattr(request, 'COOKIES'):
                event_log.session_id = request.COOKIES.get('sessionid', '')

            if hasattr(request, 'META'):
                event_log.user_ip_address = request.META.get('REMOTE_ADDR', '')
                event_log.http_referrer = request.META.get('HTTP_REFERER', '')[:255]
                event_log.http_user_agent = request.META.get('HTTP_USER_AGENT', '')
                event_log.request_method = request.META.get('REQUEST_METHOD', '')
                event_log.query_string = request.META.get('QUERY_STRING', '')

                # take care of robots
                robot = Robot.objects.get_by_agent(event_log.http_user_agent)
                if robot:
                    event_log.robot = robot

            try:
                event_log.server_ip_address = settings.INTERNAL_IPS[0]
            except:
                event_log.server_ip_address = gethostbyname(gethostname())

            if hasattr(request, 'path'):
                event_log.url = request.path or ''

        # setup instance information
        # Source may need to be a required field. The event log reports use source to
        # generate colors and use the source name on the display.
        # This will have to move forward when the eventlog ids and changes can
        # be approved with ED
        if instance:
            ct = ContentType.objects.get_for_model(instance)
            event_log.content_type = ct
            event_log.object_id = instance.pk
            event_log.source = ct.app_label
            event_log.headline = unicode(instance)[:50]

        if not event_log.source:
            event_log.source = ''

        event_log.save()

        return event_log
