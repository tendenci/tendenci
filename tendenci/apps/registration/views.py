"""
Views which allow users to create and activate accounts.

"""
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.core.exceptions import ImproperlyConfigured

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.registration.forms import RegistrationForm
from tendenci.apps.registration.models import RegistrationProfile
from tendenci.apps.perms.utils import get_notice_recipients
from tendenci.apps.base.utils import get_next_url

try:
    from tendenci.apps.notifications import models as notification
except ImproperlyConfigured:
    notification = None


def activate(request, activation_key,
             template_name='registration/activate.html',
             extra_context=None):
    """
    Activate a ``User``'s account from an activation key, if their key
    is valid and hasn't expired.

    By default, use the template ``registration/activate.html``; to
    change this, pass the name of a template as the keyword argument
    ``template_name``.

    **Required arguments**

    ``activation_key``
       The activation key to validate and use for activating the
       ``User``.

    **Optional arguments**

    ``extra_context``
        A dictionary of variables to add to the template context. Any
        callable object in this dictionary will be called to produce
        the end result which appears in the context.

    ``template_name``
        A custom template to use.

    **Context:**

    ``account``
        The ``User`` object corresponding to the account, if the
        activation was successful. ``False`` if the activation was not
        successful.

    ``expiration_days``
        The number of days for which activation keys stay valid after
        registration.

    Any extra variables supplied in the ``extra_context`` argument
    (see above).

    **Template:**

    registration/activate.html or ``template_name`` keyword argument.

    """
    next_url = get_next_url(request)
    from_memberships = next_url and next_url.startswith('/memberships/')
    activation_key = activation_key.lower() # Normalize before trying anything with it.
    account = RegistrationProfile.objects.activate_user(activation_key,
                                                        from_memberships=from_memberships)
    if account:
        account.auto_login = True
        credentials = {
            'username': '',
            'password': '',
            'user': account
        }
        user = authenticate(request, **credentials)
        login(request, user)

        # send notification to administrators
        recipients = get_notice_recipients('module', 'users', 'userrecipients')
        if recipients:
            if notification:
                extra_context = {
                    'object': user.profile,
                    'request': request,
                }
                notification.send_emails(recipients,'user_added', extra_context)

    if account and next_url:
        return HttpResponseRedirect(next_url)

    if extra_context is None:
        context = {}
    else:
        context = {k: (callable(v) and v() or v) for (k, v) in extra_context.items()}
    context['account'] = account
    context['expiration_days'] = settings.ACCOUNT_ACTIVATION_DAYS

    return render_to_resp(request=request, template_name=template_name,
                          context=context)


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
    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save(profile_callback=profile_callback)
            # success_url needs to be dynamically generated here; setting a
            # a default value using reverse() will cause circular-import
            # problems with the default URLConf for this application, which
            # imports this file.
            return HttpResponseRedirect(success_url or reverse('registration_complete'))
    else:
        form = form_class()

    if extra_context is None:
        context = {}
    context = {k: (callable(v) and v() or v) for (k, v) in extra_context}
    context['form'] = form
    return render_to_resp(request=request, template_name=template_name,
                          context=context)
