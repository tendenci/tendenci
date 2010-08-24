from os.path import basename, splitext

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.contrib import messages

from event_logs.models import EventLog
from site_settings.utils import get_setting
site_url = get_setting('site','global','siteurl')

def get_imp_message(request, user):
    """
        Get the message to post to super users via django
        message framework when they are impersonating 
        another user
    """
    query_string = ''
    imp_path = ''
    stop_path = ''
    url = site_url + request.get_full_path()
    
    # build the urls
    if 'QUERY_STRING' in request.META:
        query_string = request.META['QUERY_STRING']
        
    # search for impersonation query strings and
    # change the url to remove duplicate query strings
    if any(map(query_string.find,['impersonate','stop_impersonate'])):
        query_string = ''
        url = site_url + request.path
                
    if query_string:
        imp_path = '%s&impersonate=%s' % (url, user,)
        stop_path = '%s&_stop_impersonate=%s' % (url, user,)
    else:
        imp_path = '%s?impersonate=%s' % (url, user,)
        stop_path = '%s?_stop_impersonate=%s' % (url, user,)
        
    message_repl = (user.get_absolute_url(),
                    user,
                    imp_path,
                    stop_path,
                    user,)
    
    message = '<p>You are currently impersonating <a href="%s">%s</a>.</p>' + \
              '<p>Share this link with another administrator:<br /><em>%s</em></p>' + \
              '<p><a href="%s">Stop impersonating %s</a></p>'
    
    return message % message_repl
    
class ImpersonationMiddleware(object):
    """
        Allows you to impersonate another user. 
        Persists with sessions. 
    """
    def process_request(self, request):
        username = None
        session_impersonation = False
        message = False
        
        # stop the impersonation process
        if '_stop_impersonate' in request.GET:
            request.session['imp'] = False
            request.session['imp_u'] = None
            session_impersonation = False
            return
            
        # kill impersonation on post requests
        # it means they are adding, editing, deleting stuff
        if request.method == 'POST':
            request.session['imp'] = False
            request.session['imp_u'] = None
            session_impersonation = False
            return            
            
        # check for a session based impersonation
        if 'imp' in request.session.keys():
            session_impersonation = request.session['imp']
            
        # check for no file extension, if this is true 
        # then push the message to the message framework
        # this way it ignores css, jpg, etc
        if len(splitext(basename(request.path))[1]) == 0:
            message = True
            
        # check for session impersonation
        if session_impersonation and request.user.is_superuser:
            user = request.session['imp_u']
            current_user = request.user    
                
            request.user = user
            request.user._impersonator = current_user

            # show the impersonation message
            if message:
                messages.add_message(request, messages.INFO, get_imp_message(request,user))  
                      
        elif '_impersonate' in request.GET and request.user.is_superuser:
            username = request.GET['_impersonate']
            current_user = request.user

            try:
                new_user = None
                if username == 'anonymous':
                    new_user = AnonymousUser()
                else:
                    user = User.objects.get(username=username)
                    new_user = user
                    
                log_defaults = {
                    'event_id' : 1080000,
                    'event_data': '%s impersonated by %s' % (new_user, request.user),
                    'description': '%s impersonated' % new_user,
                    'user': request.user,
                    'request': request,
                    'instance': request.user,
                }
                EventLog.objects.log(**log_defaults)
                
                # set the session up to let it be known
                # you are impersonating
                request.session['imp'] = True
                request.session['imp_u'] = new_user
                    
                # set the person doing the impersonation
                # on the impersonated user object
                request.user = new_user
                request.user._impersonator = current_user
            
                # show the impersonation message
                if message:
                    messages.add_message(request, messages.INFO, get_imp_message(request,user)) 
            except:
                pass # user could not be found so do not imperonsate
            
                
            