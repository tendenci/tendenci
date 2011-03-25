from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages

from base.http import Http403
from perms.utils import has_perm
from subscribers.models import GroupSubscription
from forms_builder.forms.models import Form

@login_required
def subscribers(request, id, template_name="subscribers/subscribers.html"):
    form = get_object_or_404(Form, id=id)
    
    # check permission
    if not has_perm(request.user,'subscribers.change_groupsubscriptions'):
        raise Http403
    
    subscribers = GroupSubscription.objects.filter(subscriber__form=form)
        
    return render_to_response(template_name, {
                        'form':form,
                        'subscribers': subscribers,
                        },
                        context_instance=RequestContext(request))

@login_required
def delete_subscriber(request, id):
    sub = get_object_or_404(GroupSubscription, id=id)
    
    # check permission
    if not has_perm(request.user,'subscribers.delete_groupsubscriptions'):
        raise Http403
        
    sub.delete()
        
    return redirect('group.detail', sub.group.slug)
