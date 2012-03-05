from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from theme.shortcuts import themed_response as render_to_response
from base.http import Http403
from perms.utils import has_perm

from redirects.models import Redirect
from redirects.forms import RedirectForm
from redirects import dynamic_urls

@login_required
def search(request, template_name="redirects/search.html"):
    # check permission
    if not has_perm(request.user,'redirects.add_redirect'):  
        raise Http403
    
    query = request.GET.get('q', None)
    redirects = Redirect.objects.search(query, user=request.user)

    return render_to_response(template_name, {'redirects':redirects}, 
        context_instance=RequestContext(request))
    return render_to_response(template_name, {'redirects':redirects}, context_instance=RequestContext(request))

@login_required
def add(request, form_class=RedirectForm, template_name="redirects/add.html"):

    # check permission
    if not has_perm(request.user,'redirects.add_redirect'):  
        raise Http403

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            redirect = form.save(commit=False)     
            redirect.save() # get pk
            
            messages.add_message(request, messages.SUCCESS, 'Successfully added %s' % redirect)
            
            # reload the urls
            reload(dynamic_urls)
            
            return HttpResponseRedirect(reverse('redirects'))
    else:
        form = form_class()
       
    return render_to_response(template_name, {'form':form}, context_instance=RequestContext(request))

@login_required
def edit(request, id, form_class=RedirectForm, template_name="redirects/edit.html"):
    redirect = get_object_or_404(Redirect, pk=id)

    # check permission
    if not has_perm(request.user,'redirects.add_redirect'):  
        raise Http403

    form = form_class(instance=redirect)
    
    if request.method == "POST":
        form = form_class(request.POST, instance=redirect)
        if form.is_valid():
            redirect = form.save(commit=False)     
            redirect.save() # get pk
            
            messages.add_message(request, messages.SUCCESS, 'Successfully edited %s' % redirect)
 
            # reload the urls
            reload(dynamic_urls)
                       
            return HttpResponseRedirect(reverse('redirects'))
       
    return render_to_response(template_name, {'redirect': redirect,'form':form}, context_instance=RequestContext(request))

@login_required
def delete(request, id, template_name="redirects/delete.html"):
    redirect = get_object_or_404(Redirect, pk=id)

    # check permission
    if not has_perm(request.user,'redirects.delete_redirect'):  
        raise Http403

    if request.method == "POST":
        messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % redirect)
        redirect.delete()
        return HttpResponseRedirect(reverse('redirects'))

    return render_to_response(template_name, {'redirect': redirect}, 
        context_instance=RequestContext(request))
