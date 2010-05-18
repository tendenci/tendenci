# django
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

from articles.models import Article
from articles.forms import ArticleForm, ArticleEditForm
from articles.permissions import ArticlePermission

def index(request, id=None, template_name="articles/view.html"):
    if not id: return HttpResponseRedirect(reverse('article.search'))
    article = get_object_or_404(Article, pk=id)
    auth = ArticlePermission(request.user)
    
    if auth.view(article): # TODO : maybe make this a decorator
        return render_to_response(template_name, {'article': article}, 
            context_instance=RequestContext(request))
    else:
        raise Http404 # TODO : change where this goes

def search(request, template_name="articles/search.html"):
    articles = Article.objects.all()
    return render_to_response(template_name, {'articles':articles}, 
        context_instance=RequestContext(request))

def print_view(request, id, template_name="articles/print-view.html"):
    article = get_object_or_404(Article, pk=id)
    return render_to_response(template_name, {'article': article}, 
        context_instance=RequestContext(request))

@login_required
def edit(request, id, form_class=ArticleEditForm, template_name="articles/edit.html"):
    article = get_object_or_404(Article, pk=id)
    auth = ArticlePermission(request.user)
    
    if auth.edit(article): # TODO : maybe make this a decorator    
        if request.method == "POST":
            form = form_class(request.user, request.POST, instance=article)
            if form.is_valid():
                original_owner = article.owner
                article = form.save(commit=False)
                article.save()
                
                # assign creator permissions
                auth.assign(content_object=article)   
 
                # assign owner permissions
                if article.owner != original_owner:    
                    auth = ArticlePermission(article.owner)
                    auth.assign(content_object=article)  
                    if original_owner != article.creator:
                        auth = ArticlePermission(original_owner)
                        auth.remove(content_object=article)
                               
                return HttpResponseRedirect(reverse('article', args=[article.pk]))             
        else:
            form = form_class(request.user, instance=article)

        return render_to_response(template_name, {'article': article, 'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http404 # TODO : change where this goes

@login_required
def add(request, form_class=ArticleForm, template_name="articles/add.html"):
    auth = ArticlePermission(request.user)
    
    if auth.add(): # TODO : maybe make this a decorator   
        if request.method == "POST":
            form = form_class(request.user, request.POST)
            if form.is_valid():
                article = form.save(commit=False)
                
                # set up the user information
                article.creator = request.user
                article.creator_username = request.user.username
                article.owner = request.user
                article.owner_username = request.user.username
                
                article.save()
                
                # assign creator and owner permissions
                auth.assign(content_object=article)
                
                return HttpResponseRedirect(reverse('article', args=[article.pk]))
        else:
            form = form_class(request.user)
           
        return render_to_response(template_name, {'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http404 # TODO : change where this goes
    
@login_required
def delete(request, id, template_name="articles/delete.html"):
    article = get_object_or_404(Article, pk=id)

    auth = ArticlePermission(request.user)
    if auth.delete(article): # TODO : make this a decorator    
        if request.method == "POST":
            article.delete()
            return HttpResponseRedirect(reverse('article.search'))
    
        return render_to_response(template_name, {'article': article}, 
            context_instance=RequestContext(request))
    else:
        raise Http404 # TODO : change where this goes