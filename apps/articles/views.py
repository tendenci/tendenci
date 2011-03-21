from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Count

from base.http import Http403
from articles.models import Article
from articles.forms import ArticleForm
from perms.models import ObjectPermission
from perms.utils import get_notice_recipients, has_perm
from event_logs.models import EventLog
from meta.models import Meta as MetaTags
from meta.forms import MetaForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType

from perms.utils import is_admin

try:
    from notification import models as notification
except:
    notification = None

def index(request, slug=None, template_name="articles/view.html"):
    if not slug: return HttpResponseRedirect(reverse('article.search'))
    article = get_object_or_404(Article, slug=slug)

    # non-admin can not view the non-active content
    # status=0 has been taken care of in the has_perm function
    if (article.status_detail).lower() <> 'active' and (not is_admin(request.user)):
        raise Http403
    
    if has_perm(request.user, 'articles.view_article', article):
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
    articles = articles.order_by('-release_dt')

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

def print_view(request, slug, template_name="articles/print-view.html"):
    article = get_object_or_404(Article, slug=slug)    

    log_defaults = {
        'event_id' : 435001,
        'event_data': '%s (%d) viewed by %s' % (article._meta.object_name, article.pk, request.user),
        'description': '%s viewed - print view' % article._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': article,
    }
    EventLog.objects.log(**log_defaults)
       
    if has_perm(request.user,'articles.view_article', article):
        return render_to_response(template_name, {'article': article}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def edit(request, id, form_class=ArticleForm, template_name="articles/edit.html"):
    article = get_object_or_404(Article, pk=id)

    if has_perm(request.user,'articles.change_article', article):    
        if request.method == "POST":

            form = form_class(request.POST, instance=article, user=request.user)

            if form.is_valid():
                article = form.save(commit=False)

                # set up user permission
                article.allow_user_view, article.allow_user_edit = form.cleaned_data['user_perms']
                
                # assign permissions
                ObjectPermission.objects.remove_all(article)
                ObjectPermission.objects.assign_group(form.cleaned_data['group_perms'], article)
                ObjectPermission.objects.assign(article.creator, article) 
                
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
                
                messages.add_message(request, messages.INFO, 'Successfully updated %s' % article)
                                                                             
                return HttpResponseRedirect(reverse('article', args=[article.slug]))             
        else:
            form = form_class(instance=article, user=request.user)

        return render_to_response(template_name, {'article': article, 'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def edit_meta(request, id, form_class=MetaForm, template_name="articles/edit-meta.html"):

    # check permission
    article = get_object_or_404(Article, pk=id)
    if not has_perm(request.user,'articles.change_article', article):
        raise Http403

    defaults = {
        'title': article.get_title(),
        'description': article.get_description(),
        'keywords': article.get_keywords(),
        'canonical_url': article.get_canonical_url(),
    }
    article.meta = MetaTags(**defaults)

    if request.method == "POST":
        form = form_class(request.POST, instance=article.meta)
        if form.is_valid():
            article.meta = form.save() # save meta
            article.save() # save relationship
            
            messages.add_message(request, messages.INFO, 'Successfully updated meta for %s' % article)
             
            return HttpResponseRedirect(reverse('article', args=[article.slug]))
    else:
        form = form_class(instance=article.meta)

    return render_to_response(template_name, {'article': article, 'form':form}, 
        context_instance=RequestContext(request))

@login_required
def add(request, form_class=ArticleForm, template_name="articles/add.html"):
    if has_perm(request.user,'articles.add_article'):
        if request.method == "POST":
            form = form_class(request.POST, user=request.user)
            if form.is_valid():           
                article = form.save(commit=False)

                # set up the user information
                article.creator = request.user
                article.creator_username = request.user.username
                article.owner = request.user
                article.owner_username = request.user.username

                # set up user permission
                article.allow_user_view, article.allow_user_edit = form.cleaned_data['user_perms']

                article.save() # get pk

                # assign permissions for selected groups
                ObjectPermission.objects.assign_group(form.cleaned_data['group_perms'], article)
                # assign creator permissions
                ObjectPermission.objects.assign(article.creator, article) 

                article.save() # update search-index w/ permissions

                log_defaults = {
                    'event_id' : 431000,
                    'event_data': '%s (%d) added by %s' % (article._meta.object_name, article.pk, request.user),
                    'description': '%s added' % article._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': article,
                }
                EventLog.objects.log(**log_defaults)
                
                messages.add_message(request, messages.INFO, 'Successfully added %s' % article)
                
                # send notification to administrator(s) and module recipient(s)
                recipients = get_notice_recipients('module', 'articles', 'articlerecipients')
                if recipients and notification: 
                    notification.send_emails(recipients,'article_added', {
                        'object': article,
                        'request': request,
                    })

                return HttpResponseRedirect(reverse('article', args=[article.slug]))
        else:
            form = form_class(user=request.user)
           
        return render_to_response(template_name, {'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def delete(request, id, template_name="articles/delete.html"):
    article = get_object_or_404(Article, pk=id)

    if has_perm(request.user,'articles.delete_article'):   
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

            messages.add_message(request, messages.INFO, 'Successfully deleted %s' % article)

            # send notification to administrators
            recipients = get_notice_recipients('module', 'articles', 'articlerecipients')
            if recipients:
                if notification:
                    extra_context = {
                        'object': article,
                        'request': request,
                    }
                    notification.send_emails(recipients,'article_deleted', extra_context)
                            
            article.delete()
                                    
            return HttpResponseRedirect(reverse('article.search'))
    
        return render_to_response(template_name, {'article': article}, 
            context_instance=RequestContext(request))
    else:
        raise Http403


@staff_member_required
def articles_report(request):
    stats= EventLog.objects.filter(event_id=435000)\
                    .values('content_type', 'object_id', 'headline')\
                    .annotate(count=Count('pk'))\
                    .order_by('-count')
    for item in stats:
        ct = ContentType.objects.get_for_id(item['content_type'])
        assert ct.model_class() == Article
        try:
            article = Article.objects.get(pk=item['object_id'])
            item['article'] = article
            item['per_day'] = item['count'] * 1.0 / article.age().days
        except Article.DoesNotExist:
            pass
        
    return render_to_response('reports/articles.html', 
            {'stats': stats}, 
            context_instance=RequestContext(request))
