import inspect
from time import strptime
from datetime import datetime, timedelta
from operator import and_
from haystack.query import SearchQuerySet
from socket import gethostbyname, gethostname

from django.db.models import Manager
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.conf import settings
from django.utils.encoding import smart_bytes

from tendenci.apps.robots.models import Robot
from functools import reduce


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

        if f_data['user_id']:
            qs.append(Q(user=f_data['user_id']))

        if f_data['user_name']:
            qs.append(Q(username=f_data['user_name']))

        if f_data['user_ip_address']:
            qs.append(Q(user_ip_address=f_data['user_ip_address']))

        if f_data['application']:
            qs.append(Q(application=f_data['application']))

        if f_data['action']:
            qs.append(Q(action=f_data['action']))

        if f_data['object_id']:
            qs.append(Q(object_id=f_data['object_id']))

        event_logs = self.model.objects.filter(
            reduce(and_, qs)
        )

        return event_logs.order_by('-create_dt')

    def log(self, **kwargs):
        """
        Simple Example:
            from tendenci.apps.event_logs.models import EventLog
            EventLog.objects.log()
        
        If you have a Tendenci Base Object, then use the following
        
            EventLog.objects.log(instance=obj_local_var)

        """
        request, user, instance = None, None, None
        
        stack = inspect.stack()
        
        # If the request is not present in the kwargs, we try to find it
        # by inspecting the stack. We dive 3 levels if necessary. - JMO 2012-05-14
        if 'request' in kwargs:
            request = kwargs['request']
        else:
            if 'request' in inspect.getargvalues(stack[1][0]).locals:
                request = inspect.getargvalues(stack[1][0]).locals['request']
            elif 'request' in inspect.getargvalues(stack[2][0]).locals:
                request = inspect.getargvalues(stack[2][0]).locals['request']
            elif 'request' in inspect.getargvalues(stack[3][0]).locals:
                request = inspect.getargvalues(stack[3][0]).locals['request']


        # If this eventlog is being triggered by something without a request, we
        # do not want to log it. This is usually some other form of logging
        # like Contributions or perhaps Versions in the future. - JMO 2012-05-14
        if not request:
            return None

        # skip if pingdom
        if 'pingdom.com' in request.META.get('HTTP_USER_AGENT', ''):
            return None
        
        event_log = self.model()

        # Set the following fields to blank
        event_log.guid = ""
        event_log.source = ""
        event_log.event_id = 0
        event_log.event_name = ""
        event_log.event_type = ""
        event_log.event_data = ""
        event_log.category = ""

        if 'instance' in kwargs:
            instance = kwargs['instance']
            ct = ContentType.objects.get_for_model(instance)
            event_log.content_type = ct
            event_log.object_id = instance.pk
            event_log.headline = unicode(instance)[:50]
            event_log.model_name = ct.name
            event_log.application = instance.__module__
            if hasattr(instance, 'guid'):
                event_log.uuid = instance.guid

        event_log.entity = None
        if 'entity' in kwargs:
            event_log.entity = kwargs['entity']

        # Allow a description to be added in special cases like impersonation
        event_log.description = ""
        if 'description' in kwargs:
            event_log.description = kwargs['description']

        # Application is the name of the app that the event is coming from
        #
        # We get the app name via inspecting. Due to our update_perms_and_save util
        # we must filter out perms as an actual source. This is ok since there are
        # no views within perms. - JMO 2012-05-14
        if 'application' in kwargs:
            event_log.application = kwargs['application']

        if not event_log.application:
            event_log.application = inspect.getmodule(stack[1][0]).__name__
            if "perms" in event_log.application.split('.'):
                event_log.application = inspect.getmodule(stack[2][0]).__name__
                if "perms" in event_log.application.split('.'):
                    event_log.application = inspect.getmodule(stack[3][0]).__name__

        event_log.application = event_log.application.split('.')
        remove_list = ['tendenci',
                        'models',
                        'views',
                        'addons',
                        'core',
                        'apps',
                        'contrib']

        for item in remove_list:
            if item in event_log.application:
                event_log.application.remove(item)

        # Join on the chance that we are left with more than one item
        # in the list that we created
        event_log.application = ".".join(event_log.application)

        # Action is the name of the view that is being called
        #
        # We get it via the stack, but we filter out stacks that are named
        # 'save' or 'update_perms_and_save' to avoid getting the incorrect
        # view. We don't want to miss on a save method override or our own
        # updating. - JMO 2012-05-14
        if 'action' in kwargs:
            event_log.action = kwargs['action']
        else:
            event_log.action = stack[1][3]
            if stack[1][3] == "save":
                if stack[2][3] == "save" or stack[2][3] == "update_perms_and_save":
                    if stack[3][3] == "update_perms_and_save":
                        event_log.action = stack[4][3]
                    else:
                        event_log.action = stack[3][3]
                else:
                    event_log.action = stack[2][3]

        if event_log.application == "base":
            event_log.application = "homepage"

        if 'user' in kwargs:
            user = kwargs['user']
        else:
            user = request.user

        # set up the user information
        if user:
            # check for impersonation and set the correct user, descriptions, etc
            impersonated_user = getattr(user, 'impersonated_user', None)
            if impersonated_user:
                if event_log.description:
                    event_log.description = '%s (impersonating %s)' % (
                        event_log.description,
                        impersonated_user.username,
                    )
                else:
                    event_log.description = '(impersonating %s)' % (
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
                # Check for HTTP_X_REAL_IP first in case we are
                # behind a load balancer
                event_log.user_ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
                if "," in event_log.user_ip_address:
                    event_log.user_ip_address = event_log.user_ip_address.split(",")[-1].replace(" ", "")

                event_log.user_ip_address = event_log.user_ip_address[-15:]
                event_log.http_referrer = smart_bytes(request.META.get('HTTP_REFERER', '')[:255], errors='replace')
                event_log.http_user_agent = smart_bytes(request.META.get('HTTP_USER_AGENT', ''), errors='replace')
                event_log.request_method = request.META.get('REQUEST_METHOD', '')
                event_log.query_string = request.META.get('QUERY_STRING', '')

                # take care of robots
                robot = Robot.objects.get_by_agent(event_log.http_user_agent)
                if robot:
                    event_log.robot = robot

            try:
                event_log.server_ip_address = gethostbyname(gethostname())
            except:
                try:
                    event_log.server_ip_address = settings.INTERNAL_IPS[0]
                except:
                    event_log.server_ip_address = '0.0.0.0'
            if hasattr(request, 'path'):
                event_log.url = request.path or ''

        # If we have an IP address, save the event_log
        if "." in event_log.user_ip_address:
            event_log.save()
            return event_log
        else:
            return None

    def delete(self, *args, **kwargs):
        pass
