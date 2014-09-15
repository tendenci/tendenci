import datetime
import os
from datetime import timedelta
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, TemplateDoesNotExist
from django.template import Template as DTemplate
from django.template.loader import render_to_string
from django.contrib import messages
from django.http import Http404, HttpResponse
from django.utils.translation import ugettext_lazy as _
from createsend import CreateSend
from createsend import Template as CST
from createsend import Campaign as CSC
from createsend.createsend import BadRequest
from tendenci.core.perms.utils import has_perm
from tendenci.addons.campaign_monitor.models import Template, Campaign
from tendenci.addons.campaign_monitor.forms import TemplateForm, CampaignForm
from tendenci.addons.campaign_monitor.utils import temporary_id, extract_files
from tendenci.addons.campaign_monitor.utils import sync_campaigns, sync_templates
from tendenci.addons.campaign_monitor.utils import apply_template_media
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.base.http import Http403
from tendenci.core.newsletters.utils import newsletter_articles_list, newsletter_jobs_list, \
    newsletter_news_list, newsletter_pages_list

api_key = getattr(settings, 'CAMPAIGNMONITOR_API_KEY', None)
client_id = getattr(settings, 'CAMPAIGNMONITOR_API_CLIENT_ID', None)
#CreateSend.api_key = api_key
auth = {'api_key': api_key}

@login_required
def template_index(request, template_name='campaign_monitor/templates/index.html'):
    if not has_perm(request.user, 'campaign_monitor.view_template'):
        raise Http403

    templates = Template.objects.all().order_by('name')

    return render_to_response(template_name, {'templates':templates},
        context_instance=RequestContext(request))

@login_required
def template_view(request, template_id, template_name='campaign_monitor/templates/view.html'):
    template = get_object_or_404(Template, template_id=template_id)

    if not has_perm(request.user,'campaign_monitor.view_template', template):
        raise Http403

    return render_to_response(template_name, {'template':template},
        context_instance=RequestContext(request))

def template_html_original(request, template_id):
    template = get_object_or_404(Template, template_id=template_id)

    if not template.html_file:
        raise Http404

    text = template.html_file.read()
    template.html_file.close()
    response = HttpResponse(text)
    response['Content-Disposition'] = 'attachment; file=original.html'

    return response

def template_html(request, template_id):
    template = get_object_or_404(Template, template_id=template_id)

    if not template.html_file:
        raise Http404

    simplified = True

    login_content = ""
    include_login = request.GET.get('include_login', False)
    if include_login:
        login_content = render_to_string('newsletters/login.txt',
                                        context_instance=RequestContext(request))

    jumplink_content = ""
    jump_links = request.GET.get('jump_links', 1)
    if jump_links:
        jumplink_content = render_to_string('newsletters/jumplinks.txt', locals(),
                                        context_instance=RequestContext(request))

    art_content = ""
    articles = request.GET.get('articles', 1)
    articles_days = request.GET.get('articles_days', 60)
    if articles:
        articles_list, articles_content = newsletter_articles_list(request, articles_days, simplified)

    news_content = ""
    news = request.GET.get('news', 1)
    news_days = request.GET.get('news_days',30)
    if news:
        news_list, news_content = newsletter_news_list(request, news_days, simplified)

    jobs_content = ""
    jobs = request.GET.get('jobs', 1)
    jobs_days = request.GET.get('jobs_days', 30)
    if jobs:
        jobs_list, jobs_content = newsletter_jobs_list(request, jobs_days, simplified)

    pages_content = ""
    pages = request.GET.get('pages', 0)
    pages_days = request.GET.get('pages_days', 7)
    if pages:
        pages_list, pages_content = newsletter_pages_list(request, pages_days, simplified)
    try:
        from tendenci.addons.events.models import Event, Type
        events = request.GET.get('events', 1)
        events_type = request.GET.get('events_type')
        start_y, start_m, start_d = request.GET.get('event_start_dt', str(datetime.date.today())).split('-')
        event_start_dt = datetime.date(int(start_y), int(start_m), int(start_d))
        end_y, end_m, end_d = request.GET.get('event_end_dt', str(datetime.date.today() + datetime.timedelta(days=90))).split('-')
        event_end_dt = datetime.date(int(end_y), int(end_m), int(end_d))
        if events:
            #events_list = Event.objects.filter(start_dt__lt=event_end_dt, end_dt__gt=event_start_dt, status_detail='active', status=True, allow_anonymous_view=True)
            events_list = Event.objects.filter(start_dt__gte=event_start_dt,
                                               start_dt__lt=event_end_dt,
                                               status_detail='active',
                                               status=True,
                                               allow_anonymous_view=True)
            if events_type:
                events_list = events_list.filter(type__pk=events_type)
                events_type = Type.objects.filter(pk=events_type)[0]
            events_list = events_list.order_by('start_dt')
    except ImportError:
        events_list = []
        events_type = None

    text = DTemplate(apply_template_media(template))
    context = RequestContext(request,
            {
                'jumplink_content':jumplink_content,
                'login_content':login_content,
                "art_content":articles_content, # legacy usage in templates
                "articles_content":articles_content,
                "articles_list":articles_list,
                "jobs_content":jobs_content,
                "jobs_list":jobs_list,
                "news_content":news_content,
                "news_list":news_list,
                "pages_content":pages_content,
                "pages_list":pages_content,
                "events":events_list, # legacy usage in templates
                "events_list":events_list,
                "events_type":events_type
            })

    response = HttpResponse(text.render(context))
    response['Content-Disposition'] = 'attachment; file=page.html'

    return response

def template_render(request, template_id):
    template = get_object_or_404(Template, template_id=template_id)

    if not template.html_file:
        raise Http404

    simplified = True

    login_content = ""
    include_login = request.GET.get('include_login', False)
    if include_login:
        login_content = render_to_string('newsletters/login.txt',
                                        context_instance=RequestContext(request))

    jumplink_content = ""
    jump_links = request.GET.get('jump_links', 1)
    if jump_links:
        jumplink_content = render_to_string('newsletters/jumplinks.txt', locals(),
                                        context_instance=RequestContext(request))

    art_content = ""
    articles = request.GET.get('articles', 1)
    articles_days = request.GET.get('articles_days', 60)
    if articles:
        articles_list, articles_content = newsletter_articles_list(request, articles_days, simplified)

    news_content = ""
    news = request.GET.get('news', 1)
    news_days = request.GET.get('news_days',30)
    if news:
        news_list, news_content = newsletter_news_list(request, news_days, simplified)

    jobs_content = ""
    jobs = request.GET.get('jobs', 1)
    jobs_days = request.GET.get('jobs_days', 30)
    if jobs:
        jobs_list, jobs_content = newsletter_jobs_list(request, jobs_days, simplified)

    pages_content = ""
    pages = request.GET.get('pages', 0)
    pages_days = request.GET.get('pages_days', 7)
    if pages:
        pages_list, pages_content = newsletter_pages_list(request, pages_days, simplified)
    try:
        from tendenci.addons.events.models import Event, Type
        events = request.GET.get('events', 1)
        events_type = request.GET.get('events_type')
        start_y, start_m, start_d = request.GET.get('event_start_dt', str(datetime.date.today())).split('-')
        event_start_dt = datetime.date(int(start_y), int(start_m), int(start_d))
        end_y, end_m, end_d = request.GET.get('event_end_dt', str(datetime.date.today() + datetime.timedelta(days=90))).split('-')
        event_end_dt = datetime.date(int(end_y), int(end_m), int(end_d))
        if events:
            #events_list = Event.objects.filter(start_dt__lt=event_end_dt, end_dt__gt=event_start_dt, status_detail='active', status=True, allow_anonymous_view=True)
            events_list = Event.objects.filter(start_dt__gte=event_start_dt,
                                               start_dt__lt=event_end_dt,
                                               status_detail='active',
                                               status=True,
                                               allow_anonymous_view=True)
            if events_type:
                events_list = events_list.filter(type__pk=events_type)
                events_type = Type.objects.filter(pk=events_type)[0]
            events_list = events_list.order_by('start_dt')
    except ImportError:
        events_list = []
        events_type = None

    text = DTemplate(apply_template_media(template))
    context = RequestContext(request,
            {
                'jumplink_content':jumplink_content,
                'login_content':login_content,
                "art_content":articles_content, # legacy usage in templates
                "articles_content":articles_content,
                "articles_list":articles_list,
                "jobs_content":jobs_content,
                "jobs_list":jobs_list,
                "news_content":news_content,
                "news_list":news_list,
                "pages_content":pages_content,
                "pages_list":pages_content,
                "events":events_list, # legacy usage in templates
                "events_list":events_list,
                "events_type":events_type
            })

    response = HttpResponse(text.render(context))

    return response

def template_text(request, template_id):
    template = get_object_or_404(Template, template_id=template_id)

    # return dummy data temporarily
    return HttpResponse("Lorem Ipsum")

@login_required
def template_add(request, form_class=TemplateForm, template_name='campaign_monitor/templates/add.html'):

    if not has_perm(request.user,'campaign_monitor.add_template'):
        raise Http403

    if request.method == "POST":
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            #save template to generate urls
            template = form.save(commit=False)
            template.template_id = temporary_id()
            template.save()
            #set up urls
            site_url = get_setting('site', 'global', 'siteurl')

            if template.zip_file:
                if hasattr(settings, 'USE_S3_STORAGE') and settings.USE_S3_STORAGE:
                    zip_url = template.get_zip_url()
                    html_url = template.html_file.url
                else:
                    zip_url = "%s%s" % (site_url, template.get_zip_url())
                    html_url = "%s%s" % (site_url, template.get_html_url())
            else:
                zip_url = ""

            #sync with campaign monitor
            try:
                t_id = CST(auth=auth).create(
                        client_id, template.name,
                        html_url, zip_url
                    )
            except BadRequest, e:
                msg_string = 'Bad Request %s: %s' % (e.data.Code, e.data.Message)
                messages.add_message(request, messages.ERROR, _(msg_string))
                template.delete()
                return render_to_response(template_name, {'form':form},
                    context_instance=RequestContext(request))
            except Exception, e:
                msg_string = 'Error: %s' % e
                messages.add_message(request, messages.ERROR, _(msg_string))
                template.delete()
                return render_to_response(template_name, {'form':form},
                    context_instance=RequestContext(request))

            #get campaign monitor details
            t = CST(auth=auth, template_id=t_id).details()
            template.template_id = t_id
            template.name = t.Name
            template.cm_preview_url = t.PreviewURL
            template.cm_screenshot_url = t.ScreenshotURL
            template.save()

            #extract and serve files in zip
            extract_files(template)
            msg_string = 'Successfully created Template : %s' % t_id
            messages.add_message(request, messages.SUCCESS, _(msg_string))

            return redirect(template)

    else:
        form = form_class()

    return render_to_response(template_name, {'form':form},
        context_instance=RequestContext(request))

@login_required
def template_edit(request, template_id, form_class=TemplateForm, template_name='campaign_monitor/templates/edit.html'):

    template = get_object_or_404(Template, template_id=template_id)

    if not has_perm(request.user,'campaign_monitor.change_template', template):
        raise Http403

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=template)
        if form.is_valid():

            #save template to generate urls
            template = form.save()

            #set up urls
            site_url = get_setting('site', 'global', 'siteurl')

            if hasattr(settings, 'USE_S3_STORAGE') and settings.USE_S3_STORAGE:
                html_url = template.html_file.url
            else:
                html_url = str("%s%s" % (site_url, template.get_html_url()))

            if template.zip_file:
                if hasattr(settings, 'USE_S3_STORAGE') and settings.USE_S3_STORAGE:
                    zip_url = template.get_zip_url()
                else:
                    zip_url = "%s%s" % (site_url, template.get_zip_url())
            else:
                zip_url = ""

            #sync with campaign monitor
            try:
                t = CST(auth=auth, template_id = form.instance.template_id)
                t.update(str(template.name), html_url, zip_url)
            except BadRequest, e:
                msg_string = 'Bad Request %s: %s' % (e.data.Code, e.data.Message)
                messages.add_message(request, messages.ERROR, _(msg_string))
                return render_to_response(template_name, {'form':form},
                    context_instance=RequestContext(request))
            except Exception, e:
                msg_string = 'Error: %s' % e
                messages.add_message(request, messages.ERROR, _(msg_string))
                return render_to_response(template_name, {'form':form},
                    context_instance=RequestContext(request))

            #get campaign monitor details
            t = t.details()
            template.name = t.Name
            template.cm_preview_url = t.PreviewURL
            template.cm_screenshot_url = t.ScreenshotURL
            template.save()

            #extract and serve files in zip
            extract_files(template)
            msg_string = 'Successfully updated Template : %s' % template.template_id
            messages.add_message(request, messages.SUCCESS, _(msg_string))

            return redirect(template)

    else:
        form = form_class(instance=template)

    return render_to_response(template_name, {'form':form},
        context_instance=RequestContext(request))

@login_required
def template_update(request, template_id):
    """
    This method makes use of the same files to update the CM Template.
    Useful for updating data/content only and retaining design.
    """

    template = get_object_or_404(Template, template_id=template_id)

    if not has_perm(request.user,'campaign_monitor.change_template', template):
        raise Http403

    #set up urls
    site_url = get_setting('site', 'global', 'siteurl')
    html_url = unicode("%s%s"%(site_url, template.get_html_url()))
    html_url += "?jump_links=1&articles=1&articles_days=60&news=1&news_days=60&jobs=1&jobs_days=60&pages=1&pages_days=7"
    try:
        from tendenci.addons.events.models import Event, Type
        html_url += "&events=1"
        html_url += "&events_type="
        html_url += "&event_start_dt=%s" % datetime.date.today()
        end_dt = datetime.date.today() + timedelta(days=90)
        html_url += "&event_end_dt=%s" % end_dt
    except ImportError:
        pass

    if template.zip_file:
        if hasattr(settings, 'USE_S3_STORAGE') and settings.USE_S3_STORAGE:
            zip_url = unicode(template.get_zip_url())
        else:
            zip_url = unicode("%s%s"%(site_url, template.get_zip_url()))
    else:
        zip_url = unicode()

    #sync with campaign monitor
    try:
        t = CST(auth=auth, template_id = template.template_id)
        t.update(unicode(template.name), html_url, zip_url)
    except BadRequest, e:
        msg_string = 'Bad Request %s: %s' % (e.data.Code, e.data.Message)
        messages.add_message(request, messages.ERROR, _(msg_string))
        return redirect(template)
    except Exception, e:
        msg_string = 'Error: %s' % e
        messages.add_message(request, messages.ERROR, _(msg_string))
        return redirect(template)

    #get campaign monitor details
    t = t.details()
    template.name = t.Name
    template.cm_preview_url = t.PreviewURL
    template.cm_screenshot_url = t.ScreenshotURL
    template.save()
    msg_string = 'Successfully updated Template : %s' % template.template_id
    messages.add_message(request, messages.SUCCESS, _(msg_string))

    return redirect(template)

@login_required
def template_delete(request, template_id):
    template = get_object_or_404(Template, template_id=template_id)

    if not has_perm(request.user,'campaign_monitor.delete_template', template):
        raise Http403

    t_id = template.template_id

    try:
        CST(auth=auth, template_id=t_id).delete()
    except BadRequest, e:
        msg_string = 'Bad Request %s: %s' % (e.data.Code, e.data.Message)
        messages.add_message(request, messages.ERROR, _(msg_string))
        return redirect(template)
    except Exception, e:
        msg_string = 'Error: %s' % e
        messages.add_message(request, messages.ERROR, _(msg_string))
        return redirect(template)

    template.delete()
    msg_string = 'Successfully deleted Template : %s' % t_id
    messages.add_message(request, messages.SUCCESS, _(msg_string))

    return redirect("campaign_monitor.template_index")

@login_required
def template_sync(request):
    if not has_perm(request.user,'campaign_monitor.add_template'):
        raise Http403

    success = sync_templates(request)

    if success:
        messages.add_message(
            request,
            messages.SUCCESS,
            _('Successfully synced with Campaign Monitor'))

    return redirect("campaign_monitor.template_index")

@login_required
def campaign_index(request, template_name='campaign_monitor/campaigns/index.html'):
    if not has_perm(request.user, 'campaign_monitor.view_campaign'):
        raise Http403

    campaigns = Campaign.objects.all().order_by('name')

    return render_to_response(template_name, {'campaigns':campaigns},
        context_instance=RequestContext(request))

@login_required
def campaign_view(request, campaign_id, template_name='campaign_monitor/campaigns/view.html'):
    campaign = get_object_or_404(Campaign, campaign_id=campaign_id)

    if not has_perm(request.user,'campaign_monitor.view_campaign', campaign):
        raise Http403

    return render_to_response(template_name, {'campaign':campaign},
        context_instance=RequestContext(request))

@login_required
def campaign_sync(request):
    if not has_perm(request.user,'campaign_monitor.add_campaign'):
        raise Http403

    sync_campaigns()

    messages.add_message(request, messages.SUCCESS, _('Successfully synced with Campaign Monitor'))
    return redirect("campaign_monitor.campaign_index")

@login_required
def campaign_generate(request, form_class=CampaignForm, template_name='campaign_monitor/campaigns/add.html'):
    if not has_perm(request.user,'campaign_monitor.add_campaign'):
        raise Http403

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            template = form.cleaned_data['template']

            #set up urls
            site_url = get_setting('site', 'global', 'siteurl')
            html_url = unicode("%s%s"%(site_url, template.get_html_url()))
            html_url += "?jump_links=%s" % form.cleaned_data.get('jump_links')
            try:
                from tendenci.addons.events.models import Event, Type
                html_url += "&events=%s" % form.cleaned_data.get('events')
                html_url += "&events_type=%s" % form.cleaned_data.get('events_type')
                html_url += "&event_start_dt=%s" % form.cleaned_data.get('event_start_dt', '')
                html_url += "&event_end_dt=%s" % form.cleaned_data.get('event_end_dt', '')
            except ImportError:
                pass
            html_url += "&articles=%s" % form.cleaned_data.get('articles')
            html_url += "&articles_days=%s" % form.cleaned_data.get('articles_days')
            html_url += "&news=%s" % form.cleaned_data.get('news')
            html_url += "&news_days=%s" % form.cleaned_data.get('news_days')
            html_url += "&jobs=%s" % form.cleaned_data.get('jobs')
            html_url += "&jobs_days=%s" % form.cleaned_data.get('jobs_days')
            html_url += "&pages=%s" % form.cleaned_data.get('pages')
            html_url += "&pages_days=%s" % form.cleaned_data.get('pages_days')

            if template.zip_file:
                if hasattr(settings, 'USE_S3_STORAGE') and settings.USE_S3_STORAGE:
                    zip_url = unicode(template.get_zip_url())
                else:
                    zip_url = unicode("%s%s"%(site_url, template.get_zip_url()))
            else:
               zip_url = unicode()

            #sync with campaign monitor
            try:
                t = CST(auth=auth, template_id = template.template_id)
                t.update(unicode(template.name), html_url, zip_url)
            except BadRequest, e:
                messages.add_message(request, messages.ERROR, 'Bad Request %s: %s' % (e.data.Code, e.data.Message))
                return redirect('campaign_monitor.campaign_generate')
            except Exception, e:
                messages.add_message(request, messages.ERROR, 'Error: %s' % e)
                return redirect('campaign_monitor.campaign_generate')
            return redirect("%s/campaign/create/new" % settings.CAMPAIGNMONITOR_URL)

    else:
        form = form_class()

    return render_to_response(template_name,
        {'form':form},
        context_instance=RequestContext(request))


@login_required
def campaign_delete(request, campaign_id, template_name="campaign_monitor/campaigns/delete.html"):
    campaign = get_object_or_404(Campaign, campaign_id=campaign_id)

    if not has_perm(request.user,'campaign_monitor.delete_campaign'):
        raise Http403

    if request.method == "POST":

        try:
            CSC(auth=auth, campaign_id=campaign.campaign_id).delete()
        except BadRequest, e:
            msg_string = 'Bad Request %s: %s' % (e.data.Code, e.data.Message)
            messages.add_message(request, messages.ERROR, _(msg_string))
            return redirect(campaign)
        except Exception, e:
            msg_string = 'Error: %s' % e
            messages.add_message(request, messages.ERROR, _(msg_string))
            return redirect(campaign)

        campaign.delete()
        messages.add_message(request, messages.SUCCESS, _('Successfully deleted campaign.'))
        return redirect("campaign_monitor.campaign_index")

    return render_to_response(template_name, {'campaign': campaign},
            context_instance=RequestContext(request))
