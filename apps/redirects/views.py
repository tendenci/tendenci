from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from base.http import Http403
from perms.utils import has_perm, get_query_filters, has_view_perm
from site_settings.utils import get_setting
from theme.shortcuts import themed_response as render_to_response

from redirects.models import Redirect
from redirects.forms import RedirectForm
from redirects import dynamic_urls

@login_required
def search(request, template_name="redirects/search.html"):
    """
    This page lists out all redirects from newest to oldest.
    If a search index is available, this page will also
    have the option to search through redirects.
    """
    has_index = get_setting('site', 'global', 'searchindex')
    query = request.GET.get('q', None)

    if has_index and query:
        redirects = Redirect.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'redirects.add_redirect')
        redirects = Redirect.objects.filter(filters).distinct()
        if request.user.is_authenticated():
            redirects = redirects.select_related()
        redirects = redirects.order_by('-create_dt')

    # check permission
    if not has_perm(request.user,'redirects.add_redirect'):  
        raise Http403

    return render_to_response(template_name, {'redirects':redirects}, 
        context_instance=RequestContext(request))

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
