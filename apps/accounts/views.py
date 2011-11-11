
from django.conf import settings
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
#from django.contrib.auth.models import User

from registration.forms import RegistrationForm
from forms import LoginForm
from event_logs.models import EventLog
from site_settings.utils import get_setting
from base.decorators import ssl_required

@ssl_required
def login(request, form_class=LoginForm, template_name="account/login.html"):
    if request.method == "POST":
        default_redirect_to = getattr(settings, "LOGIN_REDIRECT_URLNAME", None)
        if default_redirect_to:
            default_redirect_to = reverse(default_redirect_to)
        else:
            default_redirect_to = settings.LOGIN_REDIRECT_URL
        redirect_to = request.REQUEST.get("next", "")
        # light security check -- make sure redirect_to isn't garabage.
        if not redirect_to or "://" in redirect_to or " " in redirect_to:
            redirect_to = default_redirect_to
        
        form = form_class(request.POST)
        if form.login(request):
            log_defaults = {
                'event_id' : 125200,
                'event_data': '%s (%d) logged in by form' % (request.user._meta.object_name, request.user.pk),
                'description': '%s logged in' % request.user._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': request.user,
            }
            EventLog.objects.log(**log_defaults)
            return HttpResponseRedirect(redirect_to)
    else:
        form = form_class()
    
    return render_to_response(template_name, {
        "form": form
    }, context_instance=RequestContext(request))
    
@ssl_required    
def register(request, success_url=None,
             form_class=RegistrationForm, profile_callback=None,
             template_name='registration/registration_form.html',
             extra_context=None):
    """
    Allow a new user to register an account.
    
    Following successful registration, issue a redirect; by default,
    this will be whatever URL corresponds to the named URL pattern
    ``registration_complete``, which will be
    ``/accounts/register/complete/`` if using the included URLConf. To
    change this, point that named pattern at another URL, or pass your
    preferred URL as the keyword argument ``success_url``.
    
    By default, ``registration.forms.RegistrationForm`` will be used
    as the registration form; to change this, pass a different form
    class as the ``form_class`` keyword argument. The form class you
    specify must have a method ``save`` which will create and return
    the new ``User``, and that method must accept the keyword argument
    ``profile_callback`` (see below).
    
    To enable creation of a site-specific user profile object for the
    new user, pass a function which will create the profile object as
    the keyword argument ``profile_callback``. See
    ``RegistrationManager.create_inactive_user`` in the file
    ``models.py`` for details on how to write this function.
    
    By default, use the template
    ``registration/registration_form.html``; to change this, pass the
    name of a template as the keyword argument ``template_name``.
    
    **Required arguments**
    
    None.
    
    **Optional arguments**
    
    ``form_class``
        The form class to use for registration.
    
    ``extra_context``
        A dictionary of variables to add to the template context. Any
        callable object in this dictionary will be called to produce
        the end result which appears in the context.
    
    ``profile_callback``
        A function which will be used to create a site-specific
        profile instance for the new ``User``.
    
    ``success_url``
        The URL to redirect to on successful registration.
    
    ``template_name``
        A custom template to use.
    
    **Context:**
    
    ``form``
        The registration form.
    
    Any extra variables supplied in the ``extra_context`` argument
    (see above).
    
    **Template:**
    
    registration/registration_form.html or ``template_name`` keyword
    argument.
    
    """
    # check if this site allows self registration, if not, redirect to login page
    allow_self_registration = get_setting('module', 'users', 'selfregistration')
    if not allow_self_registration:
        return HttpResponseRedirect(reverse('auth_login'))
    
    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            new_user = form.save(profile_callback=profile_callback)
            # success_url needs to be dynamically generated here; setting a
            # a default value using reverse() will cause circular-import
            # problems with the default URLConf for this application, which
            # imports this file.
            
            # add to the default group(s)
            default_user_groups =[g.strip() for g in (get_setting('module', 'users', 'defaultusergroup')).split(',')]
            if default_user_groups:
                from user_groups.models import Group, GroupMembership
                from django.db.models import Q
                for group_name in default_user_groups:
                    groups = Group.objects.filter(Q(name=group_name) | Q(label=group_name)).filter(allow_self_add=1, status=1, status_detail='active')
                    if groups:
                        group = groups[0]
                    else:
                        # group doesnot exist, so create the group
                        group = Group()
                        group.name  = group_name
                        group.label = group_name
                        group.type = 'distribution'
                        group.show_as_option = 1
                        group.allow_self_add = 1
                        group.allow_self_remove = 1
                        group.creator = new_user
                        group.creator_username = new_user.username
                        group.owner =  new_user
                        group.owner_username = new_user.username
                        try:
                            group.save()
                        except:
                            group = None
                        
                    if group:
                        gm = GroupMembership()
                        gm.group = group
                        gm.member = new_user
                        gm.creator_id = new_user.id
                        gm.creator_username = new_user.username
                        gm.owner_id =  new_user.id
                        gm.owner_username = new_user.username
                        gm.save()
 
            log_defaults = {
                'event_id' : 121000,
                'event_data': '%s (%d) self added by form' % (new_user._meta.object_name, new_user.pk),
                'description': '%s self added' % new_user._meta.object_name,
                'user': new_user,
                'request': request,
                'instance': new_user,
            }
            EventLog.objects.log(**log_defaults)
                   
            return HttpResponseRedirect(success_url or reverse('registration_complete'))
    else:
        form = form_class()
    
    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value
    return render_to_response(template_name,
                              { 'form': form },
                              context_instance=context)