import datetime

from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template import Template as DTemplate
from django.template.loader import render_to_string
from django.views.generic import TemplateView

from tendenci.core.base.http import Http403
from tendenci.addons.campaign_monitor.utils import apply_template_media
from tendenci.core.newsletters.models import NewsletterTemplate
from tendenci.core.newsletters.utils import (newsletter_articles_list, newsletter_jobs_list,
                                             newsletter_news_list, newsletter_pages_list)
from tendenci.core.perms.utils import has_perm


class NewsletterGeneratorView(TemplateView):
    template_name="newsletters/newsletter_generator.html"

    def get_context_data(self, **kwargs):
        context = super(NewsletterGeneratorView, self).get_context_data(**kwargs)
        cm_api_key = getattr(settings, 'CAMPAIGNMONITOR_API_KEY', None) 
        cm_client_id = getattr(settings, 'CAMPAIGNMONITOR_API_CLIENT_ID', None)
        if cm_api_key and cm_client_id:
            context['CAMPAIGNMONITOR_ENABLED'] = True
        else:
            context['CAMPAIGNMONITOR_ENABLED'] = False

        return context


def template_view(request, template_id, render=True):
    template = get_object_or_404(NewsletterTemplate, template_id=template_id)
    
    if not template.html_file:
        raise Http404

    if not has_perm(request.user, 'newsletters.view_newslettertemplate'):
        raise Http403

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
            events_list = Event.objects.filter(start_dt__lt=event_end_dt, end_dt__gt=event_start_dt, status_detail='active', status=True, allow_anonymous_view=True)
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
    content = text.render(context)

    if render:
        response = HttpResponse(content)
        return response
    else:
        template_name="newsletters/content.html"    
        return render_to_response(template_name, {'content': content, 'template': template,},
                                  context_instance=RequestContext(request))
