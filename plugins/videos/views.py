from django.template.context import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from base.http import Http403
from event_logs.models import EventLog
from perms.utils import has_perm
from models import Video, Category


def index(request, cat_slug=None, template_name="videos/list.html"):
    if cat_slug:
        query = 'cat:%s' % cat_slug
    else:
        query = ''
    videos = Video.objects.search(query, user=request.user)
    videos = videos.order_by('-ordering','-create_dt')

    categories = Category.objects.all()
    if cat_slug:
        category = get_object_or_404(Category, slug=cat_slug)
        
    log_defaults = {
        'event_id' : 1200400,
        'event_data': '%s viewed by %s' % ('Video list', request.user),
        'description': '%s viewed' % 'Video',
        'user': request.user,
        'request': request,
        'source': 'video',
    }
    EventLog.objects.log(**log_defaults)
    return render_to_response(template_name, locals(), 
        context_instance=RequestContext(request))
            
def search(request, cat_slug=None, template_name="videos/list.html"):
    query = request.GET.get('q', None)
    cat = request.GET.get('cat', cat_slug)
    if cat:
        cat_query = 'cat:%s' % cat
        query = ' '.join([query, cat_query])
        try:
            category = Category.objects.get(slug=cat)
        except:
            pass

    videos = Video.objects.search(query, user=request.user)
    videos = videos.order_by('-ordering','-create_dt')
    categories = Category.objects.all()   

    log_defaults = {
        'event_id' : 1200400,
        'event_data': '%s searched by %s' % ('Videos', request.user),
        'description': '%s searched' % 'Videos',
        'user': request.user,
        'request': request,
        'source': 'video',
    }
    EventLog.objects.log(**log_defaults)
    return render_to_response(template_name, locals(), 
        context_instance=RequestContext(request))


def details(request, slug, template_name="videos/details.html"):
    "Video page with embed code printed"
    
    categories = Category.objects.all()
    
    video = get_object_or_404(Video, slug=slug)

    if has_perm(request.user, 'videos.view_video', video):
        log_defaults = {
            'event_id' : 1200500,
            'event_data': '%s (%d) viewed by %s' % (video._meta.object_name, video.pk, request.user),
            'description': '%s viewed' % video._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': video,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'video': video,'categories': categories}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
