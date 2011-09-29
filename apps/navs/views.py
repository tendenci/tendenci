from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse

from base.http import Http403
from event_logs.models import EventLog
from perms.utils import has_perm, update_perms_and_save, is_admin
from navs.models import Nav
from navs.forms import NavForm

@login_required
def search(request, template_name="navs/search.html"):
    query = request.GET.get('q', None)
    navs = Nav.objects.search(query, user=request.user)
    
    log_defaults = {
        'event_id' : 195400,
        'event_data': '%s searched by %s' % ('Nav', request.user),
        'description': '%s searched' % 'Nav',
        'user': request.user,
        'request': request,
        'source': 'navs'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(
        template_name,
        {'navs':navs},
        context_instance=RequestContext(request)
    )

def detail(request, id, template_name="navs/detail.html"):
    nav = get_object_or_404(Nav, id=id)
    
    if not has_perm(request.user, 'navs.view_nave', nav):
        raise Http403
    
    return render_to_response(
        template_name,
        {'nav':nav},
        context_instance=RequestContext(request),
    )

def add(request, form_class=NavForm, template_name="navs/add.html"):
    if not has_perm(request.user, 'navs.add_nav'):
        raise Http403
    
    if request.method == "POST":
        form = form_class(request.POST, user=request.user)
        if form.is_valid():
            nav = form.save(commit=False)
            nav = update_perms_and_save(request, form, nav)
            messages.add_message(request, messages.INFO, 'Successfully added %s' % nav)
            return redirect('navs.detail', id=nav.id)
    else:
        form = form_class(user=request.user)
        
    return render_to_response(
        template_name,
        {'form':form},
        context_instance=RequestContext(request),
    )

def edit(request, id, form_class=NavForm, template_name="navs/add.html"):
    nav = get_object_or_404(Nav, id=id)
    if not has_perm(request.user, 'navs.change_nav'):
        raise Http403
    
    if request.method == "POST":
        form = form_class(request.POST, instance=nav, user=request.user)
        if form.is_valid():
            nav = form.save(commit=False)
            nav = update_perms_and_save(request, form, nav)
            messages.add_message(request, messages.INFO, 'Successfully added %s' % nav)
            return redirect('navs.detail', id=nav.id)
    else:
        form = form_class(user=request.user, instance=nav)
        
    return render_to_response(
        template_name,
        {'form':form},
        context_instance=RequestContext(request),
    )
