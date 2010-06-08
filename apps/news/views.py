from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from news.models import News
from news.forms import NewsForm

def index(request, id=None, template_name="news/view.html"):
    if not id: return HttpResponseRedirect(reverse('news.search'))
    news = get_object_or_404(News, pk=id)
    return render_to_response(template_name, {'news': news}, 
        context_instance=RequestContext(request))

def search(request, template_name="news/search.html"):
    news = News.objects.all()
    return render_to_response(template_name, {'news':news}, 
        context_instance=RequestContext(request))

def print_view(request, id, template_name="news/print-view.html"):
    news = get_object_or_404(News, pk=id)
    return render_to_response(template_name, {'news': news}, 
        context_instance=RequestContext(request))

@login_required
def edit(request, id, form_class=NewsForm, template_name="news/edit.html"):
    news = get_object_or_404(News, pk=id)
    form = form_class(instance=news)

    if request.method == "POST":
        form = form_class(request.user, request.POST, instance=news)
        if form.is_valid():
            news = form.save()

            return HttpResponseRedirect(reverse('news.view', args=[news.pk])) 

    return render_to_response(template_name, {'news': news, 'form':form}, 
        context_instance=RequestContext(request))

@login_required
def add(request, form_class=NewsForm, template_name="news/add.html"):

    if request.method == "POST":
        form = form_class(request.user, request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            
            # set up the user information
            news.creator = request.user
            news.creator_username = request.user.username
            news.owner = request.user
            news.owner_username = request.user.username
            
            news.save()
            
            return HttpResponseRedirect(reverse('news.view', args=[news.pk]))
    else:
        form = form_class(request.user)
       
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))

@login_required
def delete(request, id, template_name="news/delete.html"):
    news = get_object_or_404(News, pk=id)

    if request.method == "POST":
        news.delete()
        return HttpResponseRedirect(reverse('news.search'))

    return render_to_response(template_name, {'news': news}, 
        context_instance=RequestContext(request))