from builtins import str
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from tendenci.apps.base.http import Http403
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.meta.models import Meta as MetaTags
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.meta.forms import MetaForm
from tendenci.apps.perms.decorators import is_enabled
from tendenci.apps.perms.utils import (get_notice_recipients, has_perm,
    update_perms_and_save, get_query_filters)
from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.exports.utils import run_export_task

from tendenci.apps.news.models import News
from tendenci.apps.news.forms import NewsForm, NewsSearchForm
from tendenci.apps.notifications import models as notification
from tendenci.apps.perms.utils import assign_files_perms


@is_enabled('news')
def detail(request, slug=None, template_name="news/view.html"):
    if not slug:
        return HttpResponseRedirect(reverse('news.search'))
    news = get_object_or_404(News, slug=slug)

    # non-admin can not view the non-active content
    # status=0 has been taken care of in the has_perm function
    if (news.status_detail).lower() != 'active' and (not request.user.profile.is_superuser):
        raise Http403

    # check permission
    if not has_perm(request.user, 'news.view_news', news):
        raise Http403

    #check for release date if it's in the future or not
    if not news.is_released:
        if not request.user.is_authenticated:
            raise Http404

        if not request.user.profile.is_superuser:
            raise Http403

    EventLog.objects.log(instance=news)

    return render_to_resp(request=request, template_name=template_name,
        context={'news': news})


@is_enabled('news')
def search(request, release_year=None, template_name="news/search.html"):
    query = request.GET.get('q', None)
    form = NewsSearchForm(request.GET, user=request.user)

    if form.is_valid():
        try:
            news_group = int(form.cleaned_data.get('news_group', None))
        except:
            news_group = None

        if get_setting('site', 'global', 'searchindex') and query:
            news = News.objects.search(query, user=request.user)
            # use order (existing for all modules) for sorting cause the current
            # haystack + whoosh cannot sort by release_dt correctly
            news = news.order_by('-order')
        else:
            filters = get_query_filters(request.user, 'news.view_news')
            news = News.objects.filter(filters).distinct()
            news = news.order_by('-release_dt')
        if news_group:
            news = news.filter(groups__in=[news_group])

        if not has_perm(request.user, 'news.view_news'):
            news = news.filter(release_dt_local__lte=datetime.now())
    else:
        news = News.objects.none()

    EventLog.objects.log()

    release_years = News.objects.datetimes('release_dt', 'year', order='DESC')
    release_years_list = [rel.year for rel in release_years]

    if release_year:
        release_year = int(release_year)
        if release_year < 1900:
            raise Http404
        news = news.filter(release_dt_local__year=release_year)

    return render_to_resp(request=request, template_name=template_name,
        context={'search_news': news,
                                              'form': form,
                                              'release_year': release_year,
                                              'release_years_list': release_years_list})


def search_redirect(request):
    return HttpResponseRedirect(reverse('news'))


@is_enabled('news')
def print_view(request, slug, template_name="news/print-view.html"):
    news = get_object_or_404(News, slug=slug)

    if not has_perm(request.user, 'news.view_news', news):
        raise Http403

    EventLog.objects.log(instance=news)

    return render_to_resp(request=request, template_name=template_name,
        context={'news': news})


@is_enabled('news')
@login_required
def edit(request, id, form_class=NewsForm, template_name="news/edit.html"):
    news = get_object_or_404(News, pk=id)

    # check permission
    if not has_perm(request.user, 'news.change_news', news):
        raise Http403

    form = form_class(instance=news, user=request.user)

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=news, user=request.user)
        if form.is_valid():
            news = form.save(commit=False)

            # update all permissions and save the model
            news = update_perms_and_save(request, form, news)
            form.save_m2m()

            # save photo
            photo = form.cleaned_data['photo_upload']
            if photo:
                news.save(photo=photo)
                assign_files_perms(news, files=[news.thumbnail])

            # update thumbnail status when news status is updated
            # this will fix the error wherein a thumbnail image
            # can be viewed only when logged in.
            thumbnail = news.thumbnail
            if thumbnail:
                thumbnail.status_detail = news.status_detail
                thumbnail.save()
            msg_string = 'Successfully updated %s' % str(news)
            messages.add_message(request, messages.SUCCESS, _(msg_string))

            return HttpResponseRedirect(reverse('news.detail', args=[news.slug]))

    return render_to_resp(request=request, template_name=template_name,
        context={'news': news, 'form': form})


@is_enabled('news')
@login_required
def edit_meta(request, id, form_class=MetaForm, template_name="news/edit-meta.html"):
    # check permission
    news = get_object_or_404(News, pk=id)
    if not has_perm(request.user, 'news.change_news', news):
        raise Http403

    defaults = {
        'title': news.get_title(),
        'description': news.get_description(),
        'keywords': news.get_keywords(),
        'canonical_url': news.get_canonical_url(),
    }
    news.meta = MetaTags(**defaults)

    if request.method == "POST":
        form = form_class(request.POST, instance=news.meta)
        if form.is_valid():
            news.meta = form.save()  # save meta
            news.save()  # save relationship
            msg_string = 'Successfully updated meta for %s' % str(news)
            messages.add_message(request, messages.SUCCESS, _(msg_string))

            return HttpResponseRedirect(reverse('news.detail', args=[news.slug]))
    else:
        form = form_class(instance=news.meta)

    return render_to_resp(request=request, template_name=template_name,
        context={'news': news, 'form': form})


@is_enabled('news')
@login_required
def add(request, form_class=NewsForm, template_name="news/add.html"):
    # check permission
    if not has_perm(request.user, 'news.add_news'):
        raise Http403

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            news = form.save(commit=False)

            # update all permissions and save the model
            news = update_perms_and_save(request, form, news)
            form.save_m2m()

            # save photo
            photo = form.cleaned_data['photo_upload']
            if photo:
                news.save(photo=photo)
                assign_files_perms(news, files=[news.thumbnail])

            msg_string = 'Successfully added %s' % str(news)
            messages.add_message(request, messages.SUCCESS, _(msg_string))

            # send notification to administrators
            recipients = get_notice_recipients('module', 'news', 'newsrecipients')
            if recipients:
                if notification:
                    extra_context = {
                        'object': news,
                        'request': request,
                    }
                    notification.send_emails(recipients, 'news_added', extra_context)

            return HttpResponseRedirect(reverse('news.detail', args=[news.slug]))
    else:
        form = form_class(user=request.user)

    return render_to_resp(request=request, template_name=template_name,
        context={'form': form})


@is_enabled('news')
@login_required
def delete(request, id, template_name="news/delete.html"):
    news = get_object_or_404(News, pk=id)

    # check permission
    if not has_perm(request.user, 'news.delete_news'):
        raise Http403

    if request.method == "POST":
        msg_string = 'Successfully deleted %s' % str(news)
        messages.add_message(request, messages.SUCCESS, _(msg_string))

        # send notification to administrators
        recipients = get_notice_recipients('module', 'news', 'newsrecipients')
        if recipients:
            if notification:
                extra_context = {
                    'object': news,
                    'request': request,
                }
                notification.send_emails(recipients, 'news_deleted', extra_context)

        news.delete()
        return HttpResponseRedirect(reverse('news.search'))

    return render_to_resp(request=request, template_name=template_name,
        context={'news': news})


@is_enabled('news')
@login_required
def export(request, template_name="news/export.html"):
    """Export News"""

    if not request.user.is_superuser:
        raise Http403

    if request.method == 'POST':
        fields = [
            'guid',
            'timezone',
            'slug',
            'headline',
            'summary',
            'body',
            'source',
            'first_name',
            'last_name',
            'phone',
            'fax',
            'email',
            'website',
            'release_dt',
            'syndicate',
            'design_notes',
            'enclosure_url',
            'enclosure_type',
            'enclosure_length',
            'use_auto_timestamp',
            'tags',
            'entity',
            'categories',
        ]
        EventLog.objects.log()
        export_id = run_export_task('news', 'news', fields)
        return redirect('export.status', export_id)

    return render_to_resp(request=request, template_name=template_name, context={
    })
