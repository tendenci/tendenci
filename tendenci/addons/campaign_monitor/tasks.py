from celery.task import Task
from celery.registry import tasks
from django.contrib import messages
from django.shortcuts import redirect
from createsend import Template as CST
from tendenci.core.site_settings.utils import get_setting

class CampaignGenerateTask(Task):

    def run(self, template, **kwargs):
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
            t = CST(template_id = template.template_id)
            t.update(unicode(template.name), html_url, zip_url)
        except BadRequest, e:
            messages.add_message(request, messages.ERROR, 'Bad Request %s: %s' % (e.data.Code, e.data.Message))
            return redirect('campaign_monitor.campaign_generate')
        except Exception, e:
            messages.add_message(request, messages.ERROR, 'Error: %s' % e)
            return redirect('campaign_monitor.campaign_generate')

tasks.register(CampaignGenerateTask)
