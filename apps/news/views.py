from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from news.models import News
from news.forms import NewsForm
from base.http import Http403
from perms.models import ObjectPermission
from perms.utils import has_perm
from event_logs.models import EventLog
from meta.models import Meta as MetaTags
from meta.forms import MetaForm

from perms.utils import get_notice_recipients
try:
    from notification import models as notification
except:
    notification = None

def index(request, slug=None, template_name="news/view.html"):
    if not slug: return HttpResponseRedirect(reverse('news.search'))
    news = get_object_or_404(News, slug=slug)

    # check permission
    if not has_perm(request.user,'news.view_news',news):
        raise Http403

    log_defaults = {
        'event_id' : 305500,
        'event_data': '%s (%d) viewed by %s' % (news._meta.object_name, news.pk, request.user),
        'description': '%s viewed' % news._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': news,
    }
    EventLog.objects.log(**log_defaults)

    return render_to_response(template_name, {'news': news}, 
        context_instance=RequestContext(request))

def search(request, template_name="news/search.html"):
    query = request.GET.get('q', None)
    news = News.objects.search(query, user=request.user)

    log_defaults = {
        'event_id' : 305400,
        'event_data': '%s searched by %s' % ('News', request.user),
        'description': '%s searched' % 'News',
        'user': request.user,
        'request': request,
        'source': 'news'
    }
    EventLog.objects.log(**log_defaults)

    return render_to_response(template_name, {'news':news}, 
        context_instance=RequestContext(request))

def print_view(request, slug, template_name="news/print-view.html"):
    news = get_object_or_404(News, slug=slug)

    # check permission
    if not has_perm(request.user,'news.view_news',news):
        raise Http403

    log_defaults = {
        'event_id' : 305501,
        'event_data': '%s (%d) viewed by %s' % (news._meta.object_name, news.pk, request.user),
        'description': '%s viewed - print view' % news._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': news,
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'news': news}, 
        context_instance=RequestContext(request))

@login_required
def edit(request, id, form_class=NewsForm, template_name="news/edit.html"):
    news = get_object_or_404(News, pk=id)

    # check permission
    if not has_perm(request.user,'news.change_news',news):  
        raise Http403

    form = form_class(request.user, instance=news)

    if request.method == "POST":
        form = form_class(request.user, request.POST, instance=news)
        if form.is_valid():
            news = form.save(commit=False)

            # set up user permission
            news.allow_user_view, news.allow_user_edit = form.cleaned_data['user_perms']
            
            # assign permissions
            ObjectPermission.objects.remove_all(news)
            ObjectPermission.objects.assign_group(form.cleaned_data['group_perms'], news)
            ObjectPermission.objects.assign(news.creator, news) 

            news.save()

            log_defaults = {
                'event_id' : 305200,
                'event_data': '%s (%d) edited by %s' % (news._meta.object_name, news.pk, request.user),
                'description': '%s edited' % news._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': news,
            }
            EventLog.objects.log(**log_defaults)
            
            messages.add_message(request, messages.INFO, 'Successfully updated %s' % news)

            return HttpResponseRedirect(reverse('news.view', args=[news.slug])) 

    return render_to_response(template_name, {'news': news, 'form':form}, 
        context_instance=RequestContext(request))

@login_required
def edit_meta(request, id, form_class=MetaForm, template_name="news/edit-meta.html"):

    # check permission
    news = get_object_or_404(News, pk=id)
    if not has_perm(request.user,'news.change_news',news):
        raise Http403

    defaults = {
        'title': news.get_title(),
        'description': news.get_description(),
        'keywords': news.get_keywords(),
    }
    news.meta = MetaTags(**defaults)

    if request.method == "POST":
        form = form_class(request.POST, instance=news.meta)
        if form.is_valid():
            news.meta = form.save() # save meta
            news.save() # save relationship
            
            messages.add_message(request, messages.INFO, 'Successfully updated meta for %s' % news)
            
            return HttpResponseRedirect(reverse('news.view', args=[news.slug]))
    else:
        form = form_class(instance=news.meta)

    return render_to_response(template_name, {'news': news, 'form':form}, 
        context_instance=RequestContext(request))

@login_required
def add(request, form_class=NewsForm, template_name="news/add.html"):

    # check permission
    if not has_perm(request.user,'news.add_news'):  
        raise Http403

    if request.method == "POST":
        form = form_class(request.user, request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            
            # set up the user information
            news.creator = request.user
            news.creator_username = request.user.username
            news.owner = request.user
            news.owner_username = request.user.username

            # set up user permission
            news.allow_user_view, news.allow_user_edit = form.cleaned_data['user_perms']
                            
            news.save() # get pk

            # assign permissions for selected groups
            ObjectPermission.objects.assign_group(form.cleaned_data['group_perms'], news)
            # assign creator permissions
            ObjectPermission.objects.assign(news.creator, news) 

            news.save() # update search-index w/ permissions

            log_defaults = {
                'event_id' : 305100,
                'event_data': '%s (%d) added by %s' % (news._meta.object_name, news.pk, request.user),
                'description': '%s added' % news._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': news,
            }
            EventLog.objects.log(**log_defaults)
            
            messages.add_message(request, messages.INFO, 'Successfully added %s' % news)
            
            # send notification to administrators
            recipients = get_notice_recipients('module', 'news', 'newsrecipients')
            if recipients:
                if notification:
                    extra_context = {
                        'object': news,
                        'request': request,
                    }
                    notification.send_emails(recipients,'news_added', extra_context)
            
            return HttpResponseRedirect(reverse('news.view', args=[news.slug]))
    else:
        form = form_class(request.user)
       
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))

@login_required
def delete(request, id, template_name="news/delete.html"):
    news = get_object_or_404(News, pk=id)

    # check permission
    if not has_perm(request.user,'news.delete_news'): 
        raise Http403

    if request.method == "POST":
        log_defaults = {
            'event_id' : 305300,
            'event_data': '%s (%d) deleted by %s' % (news._meta.object_name, news.pk, request.user),
            'description': '%s deleted' % news._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': news,
        }
        EventLog.objects.log(**log_defaults)
        messages.add_message(request, messages.INFO, 'Successfully deleted %s' % news)
        
        # send notification to administrators
        recipients = get_notice_recipients('module', 'news', 'newsrecipients')
        if recipients:
            if notification:
                extra_context = {
                    'object': news,
                    'request': request,
                }
                notification.send_emails(recipients,'news_deleted', extra_context)
        
        news.delete()
        return HttpResponseRedirect(reverse('news.search'))

    return render_to_response(template_name, {'news': news}, 
        context_instance=RequestContext(request))