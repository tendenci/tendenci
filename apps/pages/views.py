# django
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import Http403
from pages.models import Page
from pages.forms import PageForm
from perms.models import ObjectPermission

def index(request, id=None, template_name="pages/view.html"):
    if not id: return HttpResponseRedirect(reverse('page.search'))
    page = get_object_or_404(Page, pk=id)

    if request.user.has_perm('pages.view_page', page):
        return render_to_response(template_name, {'page': page}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="pages/search.html"):
    pages = Page.objects.all()
    return render_to_response(template_name, {'pages':pages}, 
        context_instance=RequestContext(request))

def print_view(request, id, template_name="pages/print-view.html"):
    page = get_object_or_404(Page, pk=id)

    if request.user.has_perm('pages.view_page', page):
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

                # remove all permissions on the object
                ObjectPermission.objects.remove_all(page)
                
                # assign new permissions
                user_perms = form.cleaned_data['user_perms']
                if user_perms:
                    ObjectPermission.objects.assign(user_perms, page)               
 
                # assign creator permissions
                ObjectPermission.objects.assign(page.creator, page) 
                                                              
                return HttpResponseRedirect(reverse('page', args=[page.pk]))             
        else:
            form = form_class(request.user, instance=page)

        return render_to_response(template_name, {'page': page, 'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

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
                
                # assign permissions for selected users
                user_perms = form.cleaned_data['user_perms']
                if user_perms:
                    ObjectPermission.objects.assign(user_perms, page)
                
                # assign creator permissions
                ObjectPermission.objects.assign(page.creator, page) 
                
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
            page.delete()
            return HttpResponseRedirect(reverse('page.search'))
    
        return render_to_response(template_name, {'page': page}, 
            context_instance=RequestContext(request))
    else:
        raise Http403