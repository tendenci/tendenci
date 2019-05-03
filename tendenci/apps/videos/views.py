from django.shortcuts import get_object_or_404
from django.db.models import Q

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.base.http import Http403
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.perms.utils import has_perm, get_query_filters
from tendenci.apps.videos.models import Video, Category, VideoType
from tendenci.apps.videos.forms import VideoSearchForm


def index(request, cat_slug=None, template_name="videos/list.html"):
    """
    This page lists out all videos. The order can be customized.
    Filtering by category only works if a search index is available.
    """
    category = get_object_or_404(Category, slug=cat_slug)
    filters = get_query_filters(request.user, 'videos.view_video')
    videos = Video.objects.filter(filters).distinct()
    if request.user.is_authenticated:
        videos = videos.select_related()
    if cat_slug:
        videos = videos.filter(category__slug=cat_slug)
    videos = videos.order_by('-position', '-create_dt')

    categories = Category.objects.all()
    video_types = VideoType.objects.all()

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name,
        context=locals())

def search(request, cat_slug=None, template_name="videos/list.html"):
    """
    This page lists out all videos. The order can be customized.
    If a search index is available, this page will also
    have the option to search through videos.
    """
    form = VideoSearchForm(request.GET)

    categories = Category.objects.all()
    video_types = VideoType.objects.all()

    filters = get_query_filters(request.user, 'videos.view_video')
    videos = Video.objects.filter(filters).distinct()
    if request.user.is_authenticated:
        videos = videos.select_related()

    if form.is_valid():
        query = form.cleaned_data['q']
        cat = form.cleaned_data['cat']
        vtype = form.cleaned_data['vtype']
        if query:
            videos = videos.filter(Q(title__icontains=query)|
                                   Q(description__icontains=query))
        if cat:
            categories = Category.objects.filter(slug=cat)
            category = None
            if categories:
                category = categories[0]
            if category:
                videos = videos.filter(category=category)
        if vtype:
            vtypes = VideoType.objects.filter(slug=vtype)
            video_type = None
            if vtypes:
                video_type = vtypes[0]
            if video_type:
                videos = videos.filter(video_type=video_type)
    if get_setting('module', 'videos', 'order_by_release_dt'):
        videos = videos.order_by('-release_dt')
    else:
        videos = videos.order_by('-position', '-create_dt')

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name,
        context=locals())


def detail(request, slug, template_name="videos/details.html"):
    "Video page with embed code printed"

    categories = Category.objects.all()

    video = get_object_or_404(Video, slug=slug)

    if has_perm(request.user, 'videos.view_video', video):
        EventLog.objects.log(instance=video)

        return render_to_resp(request=request, template_name=template_name,
            context={'video': video,'categories': categories})
    else:
        raise Http403
