
from django.conf import settings
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
#from django.contrib.auth.models import User
from forms import LoginForm

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
            return HttpResponseRedirect(redirect_to)
    else:
        form = form_class()
    print form.errors.keys()
    return render_to_response(template_name, {
        "form": form
    }, context_instance=RequestContext(request))