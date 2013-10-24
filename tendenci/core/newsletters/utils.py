import os
import re
import shutil
import zipfile
import datetime
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.template.loader import render_to_string
from django.template import RequestContext
from tendenci.core.site_settings.utils import get_setting


def get_start_dt(duration_days, end_dt=None):
    if not end_dt:
        end_dt = datetime.datetime.now()
    try:
        duration_days = int(duration_days)
    except:
        duration_days = 0
    if duration_days > 0:
        start_dt = end_dt - datetime.timedelta(days=duration_days)
    else:
        start_dt = None
    return start_dt
    

def newsletter_articles_list(request, articles_days, simplified):
    articles = []
    art_content = ''
    try:
        from tendenci.addons.articles.models import Article
        end_dt = datetime.datetime.now()
        start_dt = get_start_dt(articles_days, end_dt)
        
        articles = Article.objects.filter(release_dt__lte=end_dt)
        if start_dt:
            articles = articles.filter(release_dt__gt=start_dt)
        articles = articles.filter(status_detail='active', status=True, allow_anonymous_view=True)
        articles = articles.order_by("-release_dt")
        art_content = render_to_string('newsletters/articles_list.txt', 
                                       {'articles': articles,
                                        'start_dt': start_dt,
                                        'end_dt': end_dt,
                                        'simplified':simplified},
                                       context_instance=RequestContext(request))
    except ImportError:
        pass
    return articles, art_content

def newsletter_news_list(request, news_days, simplified):
    news = []
    news_content = ''
    try:
        from tendenci.addons.news.models import News
        end_dt = datetime.datetime.now()
        start_dt = get_start_dt(news_days, end_dt)
        
        news = News.objects.filter(release_dt__lte=end_dt)
        if start_dt:
            news = news.filter(release_dt__gt=start_dt)
        news = news.filter(status_detail='active', status=True, allow_anonymous_view=True)
        news = news.order_by("-release_dt")
        news_content = render_to_string('newsletters/news_list.txt', 
                                       {'news': news,
                                        'start_dt': start_dt,
                                        'end_dt': end_dt,
                                        'simplified':simplified},
                                       context_instance=RequestContext(request))
    except ImportError:
        pass
    return news, news_content


def newsletter_pages_list(request, pages_days, simplified):
    pages = []
    page_content = ''
    try:
        from tendenci.apps.pages.models import Page
        end_dt = datetime.datetime.now()
        start_dt = get_start_dt(pages_days, end_dt)
        
        if start_dt:
            pages = Page.objects.filter(update_dt__gt=start_dt)
        else:
            pages = Page.objects.all()
        pages = pages.filter(status_detail='active', status=True, allow_anonymous_view=True)
        pages = pages.order_by("-update_dt")
        page_content = render_to_string('newsletters/pages_list.txt', 
                                       {'pages': pages,
                                        'start_dt': start_dt,
                                        'end_dt': end_dt,
                                        'simplified':simplified},
                                       context_instance=RequestContext(request))
    except ImportError:
        pass
    return pages, page_content


def newsletter_jobs_list(request, jobs_days, simplified):
    jobs = []
    job_content = ''
    try:
        from tendenci.addons.jobs.models import Job
        end_dt = datetime.datetime.now()
        start_dt = get_start_dt(jobs_days, end_dt)
        
        jobs = Job.objects.filter(activation_dt__lte=end_dt)
        if start_dt:
            jobs = jobs.filter(activation_dt__gt=start_dt)
        jobs = jobs.filter(status_detail='active', status=True, allow_anonymous_view=True)
        jobs = jobs.order_by('status_detail','list_type','-post_dt')
        job_content = render_to_string('newsletters/jobs_list.txt', 
                                       {'jobs': jobs,
                                        'start_dt': start_dt,
                                        'end_dt': end_dt,
                                        'simplified':simplified},
                                       context_instance=RequestContext(request))
    except ImportError:
        pass
    return jobs, job_content


def newsletter_events_list(request, start_dt, end_dt, simplified):
    events = []
    event_content = u''
    try:
        from tendenci.addons.events.models import Event

        events = Event.objects.filter(
            start_dt=start_dt,
            end_dt=end_dt,
            status_detail='active',
            status=True,
            allow_anonymous_view=True).order_by('start_dt')

        event_content = render_to_string(
            'newsletters/events_list.txt', {
            'events': events,
            'start_dt': start_dt,
            'end_dt': end_dt,
            'simplified':simplified},
            context_instance=RequestContext(request))

    except ImportError:
        pass
    return events, event_content


def extract_files(template):
    if template.zip_file:
        zip_file = zipfile.ZipFile(template.zip_file.file)
        if hasattr(settings, 'USE_S3_STORAGE') and settings.USE_S3_STORAGE:
            # create a tmp directory to extract the zip file
            tmp_dir = 'tmp_%d' % template.id
            path = './%s/newsletters/%s' % (tmp_dir, template.template_id)
            zip_file.extractall(path)
            # upload extracted files to s3
            for root, dirs, files in os.walk(path):
                for name in files:
                    file_path = os.path.join(root, name)
                    dst_file_path = file_path.replace('./%s/' % tmp_dir, '')
                    default_storage.save(dst_file_path,
                                ContentFile(open(file_path).read()))
            # remove the tmp directory
            shutil.rmtree(tmp_dir)
        else:
            path = os.path.join(settings.MEDIA_ROOT,
                                'newsletters',
                                template.template_id)
            zip_file.extractall(path)


def apply_template_media(template):
    """
    Prepends files in content to the media path
    of a given template's zip file contents
    """
    site_url = get_setting('site', 'global', 'siteurl')
    content = unicode(template.html_file.file.read(), "utf-8")
    pattern = r'"[^"]*?\.(?:(?i)jpg|(?i)jpeg|(?i)png|(?i)gif|(?i)bmp|(?i)tif|(?i)css)"'
    repl = lambda x: '"%s/%s/%s"' % (
        site_url,
        template.get_media_url(),
        x.group(0).replace('"', ''))
    new_content = re.sub(pattern, repl, content)
    return new_content
