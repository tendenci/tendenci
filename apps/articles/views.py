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
from site_settings.utils import get_setting

from perms.utils import update_perms_and_save, get_notice_recipients, has_perm, is_admin, get_query_filters, has_view_perm
from event_logs.models import EventLog
from meta.models import Meta as MetaTags
from meta.forms import MetaForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType

try:
    from notification import models as notification
except:
    notification = None

def index(request, slug=None, template_name="articles/view.html"):
    if not slug: return HttpResponseRedirect(reverse('articles'))
    article = get_object_or_404(Article, slug=slug)

    # non-admin can not view the non-active content
    # status=0 has been taken care of in the has_perm function
    if (article.status_detail).lower() != 'active' and (not is_admin(request.user)):
        raise Http403
    
    if has_view_perm(request.user, 'articles.view_article', article):
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


def list(request, template_name="articles/list.html"):
    get = dict(request.GET)
    query = get.pop('q', [])
    get.pop('page', None)  # pop page query string out; page ruins pagination
    query_extra = ['%s:%s' % (k,v[0]) for k,v in get.items() if v[0].strip()]
    query = ''.join(query)
    if query_extra:
        query = '%s %s' % (query, ' '.join(query_extra))

    if get_setting('site', 'global', 'searchindex') and query:
        articles = Article.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'articles.view_article')
        articles = Article.objects.filter(filters).distinct()
        if not request.user.is_anonymous():
            articles = articles.select_related()

    articles = articles.order_by('-release_dt')

    log_defaults = {
        'event_id': 434000,
        'event_data': '%s searched by %s' % ('Article', request.user),
        'description': '%s searched' % 'Article',
        'user': request.user,
        'request': request,
        'source': 'articles'
    }
    EventLog.objects.log(**log_defaults)

    # Query list of category and subcategory for dropdown filters
    category = request.GET.get('category')
    try:
        category = int(category)
    except:
        category = 0
    categories, sub_categories = Article.objects.get_categories(category=category)

    return render_to_response(template_name, {'articles': articles,'categories':categories,
        'sub_categories':sub_categories},
        context_instance=RequestContext(request))


def search(request):
    return HttpResponseRedirect(reverse('articles'))


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

                # update all permissions and save the model
                article = update_perms_and_save(request, form, article)

                log_defaults = {
                    'event_id' : 432000,
                    'event_data': '%s (%d) edited by %s' % (article._meta.object_name, article.pk, request.user),
                    'description': '%s edited' % article._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': article,
                }
                EventLog.objects.log(**log_defaults)
                
                messages.add_message(request, messages.SUCCESS, 'Successfully updated %s' % article)
                                                                             
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
            
            messages.add_message(request, messages.SUCCESS, 'Successfully updated meta for %s' % article)
             
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

                # add all permissions and save the model
                articles = update_perms_and_save(request, form, article)

                log_defaults = {
                    'event_id' : 431000,
                    'event_data': '%s (%d) added by %s' % (article._meta.object_name, article.pk, request.user),
                    'description': '%s added' % article._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': article,
                }
                EventLog.objects.log(**log_defaults)
                
                messages.add_message(request, messages.SUCCESS, 'Successfully added %s' % article)
                
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

            messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % article)

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
