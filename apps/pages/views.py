# django
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from pages.models import Page
from pages.forms import PageForm
from pages.permissions import PagePermission

def index(request, id=None, template_name="pages/view.html"):
    if not id: return HttpResponseRedirect(reverse('page.search'))
    page = get_object_or_404(Page, pk=id)
    return render_to_response(template_name, {'page': page}, 
        context_instance=RequestContext(request))

def search(request, template_name="pages/search.html"):
    pages = Page.objects.all()
    return render_to_response(template_name, {'pages':pages}, 
        context_instance=RequestContext(request))

def print_view(request, id, template_name="pages/print-view.html"):
    page = get_object_or_404(Page, pk=id)
    return render_to_response(template_name, {'page': page}, 
        context_instance=RequestContext(request))

@login_required
def edit(request, id, template_name="pages/edit.html"):
    page = get_object_or_404(Page, pk=id)
    form = PageForm(instance=page)

    if request.method == "POST":
        form = PageForm(request.POST, request.user, instance=page)
        if form.is_valid():
            page = form.save()

    return render_to_response(template_name, {'page': page, 'form':form}, 
        context_instance=RequestContext(request))

@login_required
def delete(request, id, template_name="pages/delete.html"):
    page = get_object_or_404(Page, pk=id)

    if request.method == "POST":
        page.delete()
        return HttpResponseRedirect(reverse('page.search'))

    return render_to_response(template_name, {'page': page}, 
        context_instance=RequestContext(request))