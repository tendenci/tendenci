from django.conf import settings
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404
#from django.contrib.auth.models import User
from django.contrib.auth.views import password_reset as auth_password_reset
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from tendenci.apps.registration.forms import RegistrationForm
from forms import LoginForm
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.base.decorators import ssl_required
from tendenci.apps.accounts.forms import PasswordResetForm


@ssl_required
def login(request, form_class=LoginForm, template_name="account/login.html"):

    redirect_to = request.REQUEST.get('next', u'')

    if request.method == "POST":
        default_redirect_to = getattr(settings, "LOGIN_REDIRECT_URLNAME", None)
        if default_redirect_to:
            default_redirect_to = reverse(default_redirect_to)
        else:
            default_redirect_to = settings.LOGIN_REDIRECT_URL

        # light security check -- make sure redirect_to isn't garabage.
        if not redirect_to or "://" in redirect_to or " " in redirect_to:
            redirect_to = default_redirect_to

        form = form_class(request.POST)
        if form.login(request):
            EventLog.objects.log(instance=request.user, application="accounts")

            return HttpResponseRedirect(redirect_to)
        elif form.user_exists:
            messages.add_message(
                request, messages.INFO,
                _(u"The password entered for account %(uname)s is invalid." % {
                    'uname' : form.user_exists.username }))

            return HttpResponseRedirect(reverse('auth_password_reset'))
    else:
        form = form_class()

        if request.user.is_authenticated() and redirect_to:
                return HttpResponseRedirect(redirect_to)

    return render_to_response(template_name, {
        "form": form
    }, context_instance=RequestContext(request))

@ssl_required
def register(request, success_url=None,
             form_class=RegistrationForm, profile_callback=None,
             template_name='registration/registration_form.html',
             event_id=None,
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

    form_params = {}
    if request.session.get('form_params', None):
        form_params = request.session.pop('form_params')

    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES, **form_params)
        if form.is_valid():
            # This is for including a link in the reg email back to the event viewed
            event = None
            if event_id: # the user signed up via an event
                from tendenci.apps.events.models import Event
                event = get_object_or_404(Event, pk=event_id)

            new_user = form.save(profile_callback=profile_callback, event=event)
            # success_url needs to be dynamically generated here; setting a
            # a default value using reverse() will cause circular-import
            # problems with the default URLConf for this application, which
            # imports this file.

            # add to the default group(s)
            default_user_groups =[g.strip() for g in (get_setting('module', 'users', 'defaultusergroup')).split(',')]
            if default_user_groups:
                from tendenci.apps.user_groups.models import Group, GroupMembership
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


            EventLog.objects.log(instance=new_user)

            return HttpResponseRedirect(success_url or reverse('registration_complete'))
        elif form.similar_email_found:
            messages.add_message(
                request, messages.INFO,
                _(u"An account already exists for the email %(email)s." % {
                    'email': request.POST.get('email_0') or request.POST.get('email_1')}))

            querystring = 'registration=True'
            return HttpResponseRedirect(reverse('auth_password_reset')+ "?%s" % querystring)

    else:
        allow_same_email = request.GET.get('registration_approved', False)
        form_params = {'allow_same_email' : allow_same_email }
        request.session['form_params'] = form_params
        form = form_class(**form_params)

    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value
    return render_to_response(template_name,
                              { 'form': form },
                              context_instance=context)

def password_reset(request):
    from_registration = request.GET.get('registration', False)
    extra_context = {
        'from_registration': from_registration,
    }
    return auth_password_reset(request, password_reset_form=PasswordResetForm, template_name='accounts/password_reset_form.html', extra_context= extra_context)
