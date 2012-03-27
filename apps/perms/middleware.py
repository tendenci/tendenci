from os.path import basename, splitext

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User

def get_imp_message(request, user):
    """
        Get the message to post to super users via django
        message framework when they are impersonating 
        another user
    """
    from site_settings.utils import get_setting
    site_url = get_setting('site','global','siteurl')

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
        imp_path = '%s&_impersonate=%s' % (url, user,)
        stop_path = '%s&_stop_impersonate=%s' % (url, user,)
    else:
        imp_path = '%s?_impersonate=%s' % (url, user,)
        stop_path = '%s?_stop_impersonate=%s' % (url, user,)
    
    if user.is_anonymous():
        user_url = '#'
    else:
        user_url = user.get_absolute_url()

    message_repl = (user_url,
                    user,
                    imp_path,
                    stop_path,
                    user,)
    
    message = '<p><strong>Admin Impersonation:</strong><br />You are currently impersonating <a href="%s">%s</a>.</p>' + \
              '<p>Share this link with another administrator:<br /><em>%s</em></p>' + \
              '<div class="alert-actions"><a class="btn" href="%s">Stop impersonating %s</a></div>'
    
    return message % message_repl

def get_imp_user(username, real_user):
    """
        Search for an impersonated user
        and return the user object
    """
    from perms.utils import is_developer

    user = None
    if username == 'anonymous':
        user = AnonymousUser()
    else:
        try:
            user = User.objects.get(username=username)
        except:
            pass

    # Don't allow non-developers to impersonate developers
    if not is_developer(real_user) and is_developer(user):
        return None

    return user

def stop_impersonation(session):
    """
        Reset the session of a user
        impersonating.
    """
    session['is_impersonating'] = False
    session['impersonated_user'] = None    

def log_impersonation(request, new_user):
    """
        Log the impersonation in event logs
    """
    from event_logs.models import EventLog
    log_defaults = {
        'event_id' : 1080000,
        'event_data': '%s impersonated by %s' % (new_user, request.user),
        'description': '%s impersonated' % new_user,
        'user': request.user,
        'request': request,
        'instance': request.user,
    }
    EventLog.objects.log(**log_defaults)    
        
class ImpersonationMiddleware(object):
    """
        Allows you to impersonate another user. 
        Persists with sessions. 
    """
    def process_request(self, request):
        from perms.utils import is_admin

        session_impersonation = False
        message = False
        
        # stop the impersonation process
        if '_stop_impersonate' in request.GET:
            stop_impersonation(request.session)
            return         
            
        # check for a session based impersonation
        if 'is_impersonating' in request.session.keys():
            session_impersonation = request.session['is_impersonating']
        
        # check for session impersonation
        if session_impersonation and is_admin(request.user):
            # kill impersonation on post requests
            # it means they are adding, editing, deleting stuff
            if request.method == 'POST':
                stop_impersonation(request.session)
                return   

            # check for no file extension, if this is true 
            # then push the message to the message framework
            # this way it ignores css, jpg, etc
            if len(splitext(basename(request.path))[1]) == 0:
                message = True
                    
            new_user = request.session['impersonated_user']
               
            # switch impersonated user if they request someone
            # else
            if '_impersonate' in request.GET:
                new_user = get_imp_user(request.GET['_impersonate'], request.user)
                if not new_user: 
                    stop_impersonation(request.session)
                    return
                else:
                    # log this to event logs
                    log_impersonation(request, new_user)

            # show the impersonation message
            if message:
                request.impersonation_message = get_imp_message(request,new_user)
                      
            # set the impersonated user
            request.user.impersonated_user = new_user
            
        elif '_impersonate' in request.GET and is_admin(request.user): # GET
            # kill impersonation on post requests
            # it means they are adding, editing, deleting stuff
            if request.method == 'POST':
                stop_impersonation(request.session)
                return  
            
            # check for no file extension, if this is true 
            # then push the message to the message framework
            # this way it ignores css, jpg, etc
            if len(splitext(basename(request.path))[1]) == 0:
                message = True

            new_user = get_imp_user(request.GET['_impersonate'], request.user)
            if not new_user: return                
            
            # log this to event logs
            log_impersonation(request, new_user)
            
            # set the session up to let it be known
            # you are impersonating
            request.session['is_impersonating'] = True
            request.session['impersonated_user'] = new_user
        
            # show the impersonation message
            if message:
                request.impersonation_message = get_imp_message(request,new_user)
            
            # set the impersonated user
            request.user.impersonated_user = new_user
            