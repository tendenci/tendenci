# django
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from base.http import Http403
from pages.models import Page
from pages.module_meta import PageMeta
from pages.forms import PageForm
from perms.models import ObjectPermission
from event_logs.models import EventLog
from meta.models import Meta as MetaTags
from meta.forms import MetaForm

def index(request, slug=None, template_name="pages/view.html"):
    if not slug: return HttpResponseRedirect(reverse('page.search'))
    page = get_object_or_404(Page, slug=slug)

    if request.user.has_perm('pages.view_page', page):
        log_defaults = {
            'event_id' : 585000,
            'event_data': '%s (%d) viewed by %s' % (page._meta.object_name, page.pk, request.user),
            'description': '%s viewed' % page._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': page,
        }
        EventLog.objects.log(**log_defaults)        
        
        return render_to_response(template_name, {'page': page}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="pages/search.html"):
    query = request.GET.get('q', None)
    pages = Page.objects.search(query, user=request.user)

    log_defaults = {
        'event_id' : 584000,
        'event_data': '%s searched by %s' % ('Page', request.user),
        'description': '%s searched' % 'Page',
        'user': request.user,
        'request': request,
        'source': 'pages'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'pages':pages}, 
        context_instance=RequestContext(request))

def print_view(request, slug, template_name="pages/print-view.html"):
    page = get_object_or_404(Page, pk=slug)

    if request.user.has_perm('pages.view_page', page):
        log_defaults = {
            'event_id' : 585000,
            'event_data': '%s (%d) viewed by %s' % (page._meta.object_name, page.pk, request.user),
            'description': '%s viewed' % page._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': page,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'page': page}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def edit(request, id, form_class=PageForm, template_name="pages/edit.html"):

    page = get_object_or_404(Page, pk=id)

    if request.user.has_perm('pages.change_page', page):    
        if request.method == "POST":
            form = form_class(request.user, request.POST, instance=page)
            if form.is_valid():
                page = form.save(commit=False)
                page.save()

                log_defaults = {
                    'event_id' : 582000,
                    'event_data': '%s (%d) edited by %s' % (page._meta.object_name, page.pk, request.user),
                    'description': '%s edited' % page._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': page,
                }
                EventLog.objects.log(**log_defaults)

                # remove all permissions on the object
                ObjectPermission.objects.remove_all(page)
                
                # assign new permissions
                user_perms = form.cleaned_data['user_perms']
                if user_perms:
                    ObjectPermission.objects.assign(user_perms, page)               
 
                # assign creator permissions
                ObjectPermission.objects.assign(page.creator, page) 
                
                messages.add_message(request, messages.INFO, 'Successfully updated %s' % page)
                                                              
                return HttpResponseRedirect(reverse('page', args=[page.slug]))             
        else:
            form = form_class(request.user, instance=page)

        return render_to_response(template_name, {'page': page, 'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def edit_meta(request, slug, form_class=MetaForm, template_name="pages/edit-meta.html"):

    # check permission
    page = get_object_or_404(Page, pk=id)
    if not request.user.has_perm('pages.change_page', page):
        raise Http403

    if not page.meta:
        defaults = {
            'title': PageMeta().get_meta(page, 'title'),
            'description': PageMeta().get_meta(page, 'description'),
            'keywords': PageMeta().get_meta(page, 'keywords'),
        }
        page.meta = MetaTags(**defaults)

    if request.method == "POST":
        form = form_class(request.POST, instance=page.meta)
        if form.is_valid():
            page.meta = form.save() # save meta
            page.save() # save relationship

            messages.add_message(request, messages.INFO, 'Successfully updated meta for %s' % page)
            
            return HttpResponseRedirect(reverse('page', args=[page.slug]))
    else:
        form = form_class(instance=page.meta)

    return render_to_response(template_name, {'page': page, 'form':form}, 
        context_instance=RequestContext(request))

@login_required
def add(request, form_class=PageForm, template_name="pages/add.html"):

    if request.user.has_perm('pages.add_page'):
        if request.method == "POST":
            form = form_class(request.user, request.POST)
            if form.is_valid():           
                page = form.save(commit=False)
                # set up the user information
                page.creator = request.user
                page.creator_username = request.user.username
                page.owner = request.user
                page.owner_username = request.user.username
                page.save()
 
                log_defaults = {
                    'event_id' : 581000,
                    'event_data': '%s (%d) added by %s' % (page._meta.object_name, page.pk, request.user),
                    'description': '%s added' % page._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': page,
                }
                EventLog.objects.log(**log_defaults)
               
                # assign permissions for selected users
                user_perms = form.cleaned_data['user_perms']
                if user_perms:
                    ObjectPermission.objects.assign(user_perms, page)
                
                # assign creator permissions
                ObjectPermission.objects.assign(page.creator, page) 
                
                messages.add_message(request, messages.INFO, 'Successfully added %s' % page)
                
                return HttpResponseRedirect(reverse('page', args=[page.pk]))
        else:
            form = form_class(request.user)
           
        return render_to_response(template_name, {'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def delete(request, id, template_name="pages/delete.html"):
    page = get_object_or_404(Page, pk=id)

    if request.user.has_perm('pages.delete_page'):   
        if request.method == "POST":
            log_defaults = {
                'event_id' : 583000,
                'event_data': '%s (%d) deleted by %s' % (page._meta.object_name, page.pk, request.user),
                'description': '%s deleted' % page._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': page,
            }
            EventLog.objects.log(**log_defaults)
            messages.add_message(request, messages.INFO, 'Successfully deleted %s' % page)
            page.delete()
            return HttpResponseRedirect(reverse('page.search'))
    
        return render_to_response(template_name, {'page': page}, 
            context_instance=RequestContext(request))
    else:
        raise Http403