from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages

from base.http import Http403
from perms.utils import has_perm
from event_logs.models import EventLog
from subscribers.models import GroupSubscription
from forms_builder.forms.models import Form

@login_required
def subscribers(request, id, template_name="subscribers/subscribers.html"):
    """
    Returns subscriber entries for a given form
    """
    form = get_object_or_404(Form, id=id)
    
    # check permission
    if not has_perm(request.user,'subscribers.change_groupsubscriptions'):
        raise Http403
    
    subscribers = GroupSubscription.objects.filter(subscriber__form=form)
        
    return render_to_response(template_name, {
            'form':form,
            'subscribers': subscribers,
        }, context_instance=RequestContext(request))

@login_required
def subscriber_delete(request, id, template_name="subscribers/delete.html"):
    grp_sub = get_object_or_404(GroupSubscription, id=id)
    
    # check permission
    if not has_perm(request.user,'subscribers.delete_groupsubscriptions'):
        raise Http403
        
    if request.method == 'POST':
        log_defaults = {
            'event_id' : 223000,
            'event_data': '%s (%d) deleted by %s' % (grp_sub._meta.object_name, grp_sub.pk, request.user),
            'description': '%s deleted' % grp_sub._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': grp_sub,
        }
        EventLog.objects.log(**log_defaults)
        messages.add_message(request, messages.SUCCESS, 'Successfully removed subscriber %s (%s) from group %s' % (grp_sub.name, grp_sub.email, grp_sub.group))
        grp_sub.delete()
        return HttpResponseRedirect(grp_sub.group.get_absolute_url())
    return render_to_response(template_name, {
            'grp_sub': grp_sub,
        }, context_instance=RequestContext(request))

@login_required
def subscriber_detail(request, id, template_name="subscribers/detail.html"):
    """
    View that considers non custom form generated subscription for a single subscriber.
    """
    grp_sub = get_object_or_404(GroupSubscription, pk=id)
    
    # check permission
    if not has_perm(request.user,'subscribers.change_groupsubscriptions'):
        raise Http403
        
    return render_to_response(template_name, {
            'grp_sub': grp_sub,
        }, context_instance=RequestContext(request))
