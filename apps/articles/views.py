from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

from base.http import Http403
from articles.models import Article
from articles.forms import ArticleForm, ArticleEditForm
from perms.models import ObjectPermission

def index(request, id=None, template_name="articles/view.html"):
    if not id: return HttpResponseRedirect(reverse('article.search'))
    article = get_object_or_404(Article, pk=id)

    if request.user.has_perm('articles.view_article', article):
        return render_to_response(template_name, {'article': article}, 
            context_instance=RequestContext(request))
    else:
        raise Http403 # TODO : change where this goes

def search(request, template_name="articles/search.html"):
    articles = Article.objects.all()
    return render_to_response(template_name, {'articles':articles}, 
        context_instance=RequestContext(request))

def print_view(request, id, template_name="articles/print-view.html"):
    article = get_object_or_404(Article, pk=id)
     
    if request.user.has_perm('articles.view_article', article):
        return render_to_response(template_name, {'article': article}, 
            context_instance=RequestContext(request))
    else:
        raise Http403 # TODO : change where this goes
    
@login_required
def edit(request, id, form_class=ArticleEditForm, template_name="articles/edit.html"):
    article = get_object_or_404(Article, pk=id)
    original_owner = article.owner
    
    if request.user.has_perm('articles.change_article', article):    
        if request.method == "POST":
            form = form_class(request.user, request.POST, instance=article)
            if form.is_valid():
                article = form.save(commit=False)
                article.save()
                
                # assign creator permissions
                ObjectPermission.objects.assign(article.creator, article)   

                # assign owner permissions
                if article.owner != original_owner:  
                    ObjectPermission.objects.assign(article.owner, article)  
                    if original_owner != article.creator:
                        ObjectPermission.objects.remove(original_owner, article)
                               
                return HttpResponseRedirect(reverse('article', args=[article.pk]))             
        else:
            form = form_class(request.user, instance=article)

        return render_to_response(template_name, {'article': article, 'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403 # TODO : change where this goes

@login_required
def add(request, form_class=ArticleForm, template_name="articles/add.html"):
    if request.user.has_perm('articles.add_article'):
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
                
                # assign creator permissions
                ObjectPermission.objects.assign(article.creator, article) 
                
                return HttpResponseRedirect(reverse('article', args=[article.pk]))
        else:
            form = form_class(request.user)
           
        return render_to_response(template_name, {'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403 # TODO : change where this goes
    
@login_required
def delete(request, id, template_name="articles/delete.html"):
    article = get_object_or_404(Article, pk=id)

    if request.user.has_perm('articles.delete_article'):   
        if request.method == "POST":
            article.delete()
            return HttpResponseRedirect(reverse('article.search'))
    
        return render_to_response(template_name, {'article': article}, 
            context_instance=RequestContext(request))
    else:
        raise Http404 # TODO : change where this goes