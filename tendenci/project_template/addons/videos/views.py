from django.template.context import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from tendenci.core.base.http import Http403
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.event_logs.models import EventLog
from tendenci.core.perms.utils import has_perm, get_query_filters, has_view_perm
from addons.videos.models import Video, Category


def index(request, cat_slug=None, template_name="videos/list.html"):
    """
    This page lists out all videos. The order can be customized.
    Filtering by category only works if a search index is available.
    """
    category = get_object_or_404(Category, slug=cat_slug)
    filters = get_query_filters(request.user, 'videos.view_video')
    videos = Video.objects.filter(filters).distinct()
    if request.user.is_authenticated():
        videos = videos.select_related()
    if cat_slug:
        videos = videos.filter(category__slug=cat_slug)
    videos = videos.order_by('-ordering', '-create_dt')

    categories = Category.objects.all()

    EventLog.objects.log()

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
    cat = request.GET.get('cat', cat_slug)

    if has_index and query:
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

    EventLog.objects.log()

    return render_to_response(template_name, locals(), 
        context_instance=RequestContext(request))


def detail(request, slug, template_name="videos/details.html"):
    "Video page with embed code printed"
    
    categories = Category.objects.all()
    
    video = get_object_or_404(Video, slug=slug)

    if has_perm(request.user, 'videos.view_video', video):
        EventLog.objects.log(instance=video)

        return render_to_response(template_name, {'video': video,'categories': categories}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
