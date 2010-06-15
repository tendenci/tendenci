from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from news.models import News
from news.forms import NewsForm
from base.http import Http403
from perms.models import ObjectPermission
from event_logs.models import EventLog

def index(request, id=None, template_name="news/view.html"):
    if not id: return HttpResponseRedirect(reverse('news.search'))
    news = get_object_or_404(News, pk=id)

    # check permission
    if not request.user.has_perm('news.view_news', news):
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
    news = News.objects.search(query)

    log_defaults = {
        'event_id' : 305400,
        'event_data': '%s searched by %s' % ('News', request.user),
        'description': '%s searched' % 'News',
        'user': request.user,
        'request': request,
    }
    EventLog.objects.log(**log_defaults)

    return render_to_response(template_name, {'news':news}, 
        context_instance=RequestContext(request))

def print_view(request, id, template_name="news/print-view.html"):
    news = get_object_or_404(News, pk=id)

    # check permission
    if not request.user.has_perm('news.view_news', news):
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

@login_required
def edit(request, id, form_class=NewsForm, template_name="news/edit.html"):
    news = get_object_or_404(News, pk=id)

    # check permission
    if not request.user.has_perm('news.change_news', news):  
        raise Http403

    form = form_class(instance=news)

    if request.method == "POST":
        form = form_class(request.user, request.POST, instance=news)
        if form.is_valid():
            news = form.save()

            log_defaults = {
                'event_id' : 305200,
                'event_data': '%s (%d) edited by %s' % (news._meta.object_name, news.pk, request.user),
                'description': '%s edited' % news._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': news,
            }
            EventLog.objects.log(**log_defaults)

            # remove all permissions on the object
            ObjectPermission.objects.remove_all(news)

            # assign new permissions
            user_perms = form.cleaned_data['user_perms']
            if user_perms: ObjectPermission.objects.assign(user_perms, file)               

            # assign creator permissions
            ObjectPermission.objects.assign(news.creator, news)

            return HttpResponseRedirect(reverse('news.view', args=[news.pk])) 

    return render_to_response(template_name, {'news': news, 'form':form}, 
        context_instance=RequestContext(request))

@login_required
def add(request, form_class=NewsForm, template_name="news/add.html"):

    # check permission
    if not request.user.has_perm('news.add_news'):  
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
            news.save()

            log_defaults = {
                'event_id' : 305100,
                'event_data': '%s (%d) added by %s' % (news._meta.object_name, news.pk, request.user),
                'description': '%s added' % news._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': news,
            }
            EventLog.objects.log(**log_defaults)

            # assign permissions for selected users
            user_perms = form.cleaned_data['user_perms']
            if user_perms: ObjectPermission.objects.assign(user_perms, news)
            
            # assign creator permissions
            ObjectPermission.objects.assign(news.creator, news)
            
            return HttpResponseRedirect(reverse('news.view', args=[news.pk]))
    else:
        form = form_class(request.user)
       
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))

@login_required
def delete(request, id, template_name="news/delete.html"):
    news = get_object_or_404(News, pk=id)

    # check permission
    if not request.user.has_perm('news.delete_news'): 
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
        news.delete()
        return HttpResponseRedirect(reverse('news.search'))

    return render_to_response(template_name, {'news': news}, 
        context_instance=RequestContext(request))