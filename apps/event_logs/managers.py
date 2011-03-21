from time import strptime
from datetime import datetime, timedelta

from socket import gethostbyname, gethostname
from django.db.models import Manager
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AnonymousUser

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
        sqs = SearchQuerySet()
        
        q = query.get('q','')
        range = query.get('range',None)
            
        if query:
            if range:
                try:
                    date = datetime(*strptime(q,"%Y-%m-%d %H:%M:%S")[0:5])
                    start_dt = date - timedelta(minutes=2)
                    end_dt = date + timedelta(minutes=2)
                    sqs = sqs.filter(create_dt__lte=end_dt)
                    sqs = sqs.filter(create_dt__gte=start_dt)
                except:
                    sqs = sqs.auto_query(sqs.query.clean(q)) 
            else:
                sqs = sqs.auto_query(sqs.query.clean(q)) 
        else:
            sqs = sqs.all()

        sqs = sqs.order_by('-create_dt')
        
        return sqs.models(self.model)

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
        
        if not event_log.category: event_log.category = 'application'
        if not event_log.event_name: event_log.event_name = 'application'
        if not event_log.event_type: event_log.event_type = 'information'
        
        # set up the user information
        if user:
            # check for impersonation and set the correct user, descriptions, etc
            impersonated_user = getattr(user,'impersonated_user', None)
            if impersonated_user:
                event_log.event_data = '%s (impersonating %s)' % (event_log.event_data, impersonated_user.username,)
                
            if isinstance(user,AnonymousUser):
                event_log.username = 'anonymous'
            else:    
                event_log.user = user
                event_log.username = user.username
                event_log.email = user.email
    
        # setup request meta information
        if request:
            if hasattr(request,'COOKIES'):
                event_log.session_id = request.COOKIES.get('sessionid','')
                
            if hasattr(request,'META'):
                event_log.user_ip_address = request.META.get('REMOTE_ADDR','')
                event_log.http_referrer = request.META.get('HTTP_REFERER','')[:255]
                event_log.http_user_agent = request.META.get('HTTP_USER_AGENT','')
                event_log.request_method = request.META.get('REQUEST_METHOD','')
                event_log.query_string = request.META.get('QUERY_STRING','')
                
                # take care of robots
                robot = Robot.objects.get_by_agent(event_log.http_user_agent)
                if robot:
                    event_log.robot = robot
                    
            event_log.server_ip_address = gethostbyname(gethostname()) 
            
            if hasattr(request,'path'):
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
        
        if not event_log.source: event_log.source = ''
        
        event_log.save()

        return event_log