from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.base.http import Http403
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.perms.utils import has_perm, get_query_filters, update_perms_and_save, get_notice_recipients
from tendenci.apps.videos.models import Video, Category, VideoType
from tendenci.apps.videos.forms import VideoSearchForm, VideoFrontEndForm
from tendenci.apps.notifications import models as notification


@login_required
def add(request, form_class=VideoFrontEndForm, template_name="videos/edit.html"):
    # check permission
    if not has_perm(request.user, 'videos.add_video'):
        raise Http403

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            video = form.save(commit=False)
            video.creator = request.user
            video.creator_username = request.user.username
            if not request.user.is_superuser:
                video.status_detail = 'pending'

            # update all permissions and save the model
            video = update_perms_and_save(request, form, video)
            form.save_m2m()

            msg_string = _(f'Successfully added {str(video)}')
            if not request.user.is_superuser:
                msg_string += _('... Pending on Admin approval.')
            messages.add_message(request, messages.SUCCESS, msg_string)
            
            # send notification to administrator(s) and module recipient(s)
            recipients = get_notice_recipients('module', 'videos', 'videorecipients')
            if recipients and notification:
                notification.send_emails(recipients, 'video_added', {
                    'object': video,
                    'request': request,
                })

            return HttpResponseRedirect(reverse('video.details', args=[video.slug]))
    else:
        form = form_class(user=request.user)

    return render_to_resp(request=request,
                          template_name=template_name,
        context={'form': form,
                 'edit_mode': False})


@login_required
def edit(request, id, form_class=VideoFrontEndForm, template_name="videos/edit.html"):
    video = get_object_or_404(Video, pk=id)

    # check permission
    if not has_perm(request.user, 'videos.change_video', video):
        raise Http403

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=video, user=request.user)
        if form.is_valid():
            video = form.save(commit=False)

            # update all permissions and save the model
            video = update_perms_and_save(request, form, video)
            form.save_m2m()

            msg_string = _(f'Successfully updated {str(video)}')
            messages.add_message(request, messages.SUCCESS, msg_string)

            return HttpResponseRedirect(reverse('video.details', args=[video.slug]))
    else:
        form = form_class(instance=video, user=request.user)

    return render_to_resp(request=request,
                          template_name=template_name,
        context={'video': video, 'form': form,
                 'edit_mode': True})


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
