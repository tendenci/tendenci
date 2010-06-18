from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import Http403
from articles.models import Article
from articles.forms import ArticleForm
from perms.models import ObjectPermission
from event_logs.models import EventLog

def index(request, id=None, template_name="articles/view.html"):
    if not id: return HttpResponseRedirect(reverse('article.search'))
    article = get_object_or_404(Article, pk=id)
    
    if request.user.has_perm('articles.view_article', article):
        log_defaults = {
            'event_id' : 435000,
            'event_data': '%s (%d) viewed by %s' % (article._meta.object_name, article.pk, request.user),
            'description': '%s viewed' % article._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': article,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'article': article}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="articles/search.html"):
    query = request.GET.get('q', None)
    articles = Article.objects.search(query, user=request.user)

    log_defaults = {
        'event_id' : 434000,
        'event_data': '%s searched by %s' % ('Article', request.user),
        'description': '%s searched' % 'Article',
        'user': request.user,
        'request': request,
        'source': 'articles'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'articles':articles}, 
        context_instance=RequestContext(request))

def print_view(request, id, template_name="articles/print-view.html"):
    article = get_object_or_404(Article, pk=id)    

    log_defaults = {
        'event_id' : 435000,
        'event_data': '%s (%d) viewed by %s' % (article._meta.object_name, article.pk, request.user),
        'description': '%s viewed' % article._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': article,
    }
    EventLog.objects.log(**log_defaults)
       
    if request.user.has_perm('articles.view_article', article):
        return render_to_response(template_name, {'article': article}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def edit(request, id, form_class=ArticleForm, template_name="articles/edit.html"):
    article = get_object_or_404(Article, pk=id)

    if request.user.has_perm('articles.change_article', article):    
        if request.method == "POST":
            form = form_class(request.user, request.POST, instance=article)
            if form.is_valid():
                article = form.save(commit=False)
                article.save()

                log_defaults = {
                    'event_id' : 432000,
                    'event_data': '%s (%d) edited by %s' % (article._meta.object_name, article.pk, request.user),
                    'description': '%s edited' % article._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': article,
                }
                EventLog.objects.log(**log_defaults)
                
                # remove all permissions on the object
                ObjectPermission.objects.remove_all(article)
                
                # assign new permissions
                user_perms = form.cleaned_data['user_perms']
                if user_perms:
                    ObjectPermission.objects.assign(user_perms, article)               
 
                # assign creator permissions
                ObjectPermission.objects.assign(article.creator, article) 
                                                              
                return HttpResponseRedirect(reverse('article', args=[article.pk]))             
        else:
            form = form_class(request.user, instance=article)

        return render_to_response(template_name, {'article': article, 'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

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
 
                log_defaults = {
                    'event_id' : 431000,
                    'event_data': '%s (%d) added by %s' % (article._meta.object_name, article.pk, request.user),
                    'description': '%s added' % article._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': article,
                }
                EventLog.objects.log(**log_defaults)
                               
                # assign permissions for selected users
                user_perms = form.cleaned_data['user_perms']
                if user_perms:
                    ObjectPermission.objects.assign(user_perms, article)
                
                # assign creator permissions
                ObjectPermission.objects.assign(article.creator, article) 
                
                return HttpResponseRedirect(reverse('article', args=[article.pk]))
        else:
            form = form_class(request.user)
           
        return render_to_response(template_name, {'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def delete(request, id, template_name="articles/delete.html"):
    article = get_object_or_404(Article, pk=id)

    if request.user.has_perm('articles.delete_article'):   
        if request.method == "POST":
            log_defaults = {
                'event_id' : 433000,
                'event_data': '%s (%d) deleted by %s' % (article._meta.object_name, article.pk, request.user),
                'description': '%s deleted' % article._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': article,
            }
            
            EventLog.objects.log(**log_defaults)
            
            article.delete()
                
            return HttpResponseRedirect(reverse('article.search'))
    
        return render_to_response(template_name, {'article': article}, 
            context_instance=RequestContext(request))
    else:
        raise Http403