from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.http import urlquote
from django.http import HttpResponseRedirect

from base.http import Http403
from perms.utils import is_admin, is_developer

class PageSecurityCheck(object):
    """
        a decorator to check page security, and redirect accordingly
    """
    def __init__(self, security_level):
        self.page_security_level = security_level.lower()

    def __call__(self, f):
        def check_security(request, *args, **kwargs):
            
            user_security_level = 'anonymous'
            
            if request.user.is_authenticated():
                if is_developer(request.user):
                    user_security_level = 'developer'
                elif is_admin(request.user):
                    user_security_level = 'administrator'
                else:
                    user_security_level = 'user'
            
            boo = False        
            if self.page_security_level == 'anonymous':
                boo = True
            elif self.page_security_level == 'user':
                if user_security_level <> 'anonymous':
                    boo = True
            elif self.page_security_level == 'administrator':
                if user_security_level == 'administrator' or user_security_level == 'developer':
                    boo = True
            elif self.page_security_level == 'developer':
                if user_security_level == 'developer':
                    boo = True
                    
            if boo:
                # if request.user.is_authenticated(), log an event here
                return f(request, *args, **kwargs)
            else:
                if request.user.is_authenticated():
                    raise Http403
                else:
                    # redirect to login page
                    redirect_field_name=REDIRECT_FIELD_NAME
                    login_url = settings.LOGIN_URL
                    path = urlquote(request.get_full_path())
                    tup = login_url, redirect_field_name, path
                    
                    return HttpResponseRedirect('%s?%s=%s' % tup)
                    #return f(request, *args, **kwargs)
        return check_security

def admin_required(view_method):
    """
    Checks for admin permissions before
    returning method, else raises 403 exception.
    """
    def decorator(request, *args, **kwargs):
        admin = is_admin(request.user)

        if not admin:
            raise Http403
        
        return view_method(request, *args, **kwargs)

    return decorator