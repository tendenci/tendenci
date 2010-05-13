# django
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from articles.models import Article
from articles.forms import ArticleForm

def index(request, id=None, template_name="articles/view.html"):
    if not id: return HttpResponseRedirect(reverse('article.search'))
    article = get_object_or_404(Article, pk=id)
    return render_to_response(template_name, {'article': article}, 
        context_instance=RequestContext(request))

def search(request, template_name="articles/search.html"):
    articles = Article.objects.all()
    return render_to_response(template_name, {'articles':articles}, 
        context_instance=RequestContext(request))

def print_view(request, id, template_name="articles/print-view.html"):
    article = get_object_or_404(Article, pk=id)
    return render_to_response(template_name, {'article': article}, 
        context_instance=RequestContext(request))

@login_required
def edit(request, id, template_name="articles/edit.html"):
    article = get_object_or_404(Article, pk=id)
    form = ArticleForm(instance=article)

    if request.method == "POST":
        form = ArticleForm(request.POST, request.user, instance=article)
        if form.is_valid():
            article = form.save()

    return render_to_response(template_name, {'article': article, 'form':form}, 
        context_instance=RequestContext(request))

@login_required
def delete(request, id, template_name="articles/delete.html"):
    article = get_object_or_404(Article, pk=id)

    if request.method == "POST":
        article.delete()
        return HttpResponseRedirect(reverse('article.search'))

    return render_to_response(template_name, {'article': article}, 
        context_instance=RequestContext(request))