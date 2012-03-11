from django.template.context import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from base.http import Http403
from site_settings.utils import get_setting
from event_logs.models import EventLog
from perms.utils import has_perm, get_query_filters, has_view_perm
from models import Video, Category


def index(request, cat_slug=None, template_name="videos/list.html"):
    """
    This page lists out all videos. The order can be customized.
    Filtering by category only works if a search index is available.
    """
    has_index = get_setting('site', 'global', 'searchindex')

    if has_index and cat_slug:
        videos = Video.objects.search('cat:%s' % cat_slug, user=request.user)
        videos = videos.order_by('-ordering','-create_dt')
        category = get_object_or_404(Category, slug=cat_slug)
    else:
        filters = get_query_filters(request.user, 'videos.view_video')
        videos = Video.objects.filter(filters).distinct()
        if request.user.is_authenticated():
            videos = videos.select_related()
        videos = videos.order_by('-ordering', '-create_dt')

    categories = Category.objects.all()

    EventLog.objects.log(**{
        'event_id' : 1200400,
        'event_data': '%s viewed by %s' % ('Video list', request.user),
        'description': '%s viewed' % 'Video',
        'user': request.user,
        'request': request,
        'source': 'video',
    })

    return render_to_response(template_name, locals(), 
        context_instance=RequestContext(request))
            
def search(request, cat_slug=None, template_name="videos/list.html"):
    """
    This page lists out all videos. The order can be customized.
    If a search index is available, this page will also
    have the option to search through videos.
    """
    has_index = get_setting('site', 'global', 'searchindex')
    query = request.GET.get('q', None)

    categories = Category.objects.all()

    if has_index and query:
        cat = request.GET.get('cat', cat_slug)
        if cat:
            cat_query = 'cat:%s' % cat
            query = ' '.join([query, cat_query])
            categories = Category.objects.filter(slug=cat)
            category = None
            if categories:
                category = category[0]
        videos = Video.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'videos.view_video')
        videos = Video.objects.filter(filters).distinct()
        if request.user.is_authenticated():
            videos = videos.select_related()
        videos = videos.order_by('-ordering', '-create_dt')

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
