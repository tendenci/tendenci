from builtins import str
import os
import re
import shutil
import zipfile
import datetime
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.core.mail import get_connection
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.events.models import Type
from tendenci.apps.theme.utils import get_theme_search_order, get_theme_root


def get_type_choices():
    types_list = [(u'',_(u'All'))]
    types = Type.objects.all()
    for type in types:
        types_list.append((int(type.pk),type.name))

    return tuple(types_list)


def get_default_template_choices():
    newsletters_relative_path = 'newsletters/templates/default/'
    default_templates = []
    for cur_theme in get_theme_search_order():
        template_path = os.path.join(get_theme_root(cur_theme),
            'templates', newsletters_relative_path)
        if os.path.isdir(template_path):
            default_templates += os.listdir(template_path)
    default_templates = list(set(default_templates))
    default_templates.sort()
    template_choices = []
    for template in default_templates:
        template_choices.append((newsletters_relative_path + template, os.path.splitext(template)[0]))
    return template_choices

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


def get_newsletter_connection():
    return get_connection(backend=settings.NEWSLETTER_EMAIL_BACKEND)


def is_newsletter_relay_set():
    return all([settings.NEWSLETTER_EMAIL_HOST,
                settings.NEWSLETTER_EMAIL_HOST_USER,
                settings.NEWSLETTER_EMAIL_HOST_PASSWORD])


def newsletter_articles_list(request, articles_days, simplified):
    articles = []
    art_content = ''
    try:
        from tendenci.apps.articles.models import Article
        end_dt = datetime.datetime.now()
        start_dt = get_start_dt(articles_days, end_dt)

        articles = Article.objects.filter(release_dt__lte=end_dt)
        if start_dt:
            articles = articles.filter(release_dt__gt=start_dt)
        articles = articles.filter(status_detail='active', status=True, allow_anonymous_view=True)
        articles = articles.order_by("-release_dt")
        art_content = render_to_string(template_name='newsletters/articles_list.txt',
                                       context={'articles': articles,
                                        'start_dt': start_dt,
                                        'end_dt': end_dt,
                                        'simplified':simplified},
                                       request=request)
    except ImportError:
        pass
    return articles, art_content

def newsletter_news_list(request, news_days, simplified):
    news = []
    news_content = ''
    try:
        from tendenci.apps.news.models import News
        end_dt = datetime.datetime.now()
        start_dt = get_start_dt(news_days, end_dt)

        news = News.objects.filter(release_dt__lte=end_dt)
        if start_dt:
            news = news.filter(release_dt__gt=start_dt)
        news = news.filter(status_detail='active', status=True, allow_anonymous_view=True)
        news = news.order_by("-release_dt")
        news_content = render_to_string(template_name='newsletters/news_list.txt',
                                       context={'news': news,
                                        'start_dt': start_dt,
                                        'end_dt': end_dt,
                                        'simplified':simplified},
                                       request=request)
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
        page_content = render_to_string(template_name='newsletters/pages_list.txt',
                                       context={'pages': pages,
                                        'start_dt': start_dt,
                                        'end_dt': end_dt,
                                        'simplified':simplified},
                                       request=request)
    except ImportError:
        pass
    return pages, page_content


def newsletter_jobs_list(request, jobs_days, simplified):
    jobs = []
    job_content = ''
    try:
        from tendenci.apps.jobs.models import Job
        end_dt = datetime.datetime.now()
        start_dt = get_start_dt(jobs_days, end_dt)

        jobs = Job.objects.filter(activation_dt__lte=end_dt)
        if start_dt:
            jobs = jobs.filter(activation_dt__gt=start_dt)
        jobs = jobs.filter(status_detail='active', status=True, allow_anonymous_view=True)
        jobs = jobs.order_by('status_detail','list_type','-post_dt')
        job_content = render_to_string(template_name='newsletters/jobs_list.txt',
                                       context={'jobs': jobs,
                                        'start_dt': start_dt,
                                        'end_dt': end_dt,
                                        'simplified':simplified},
                                       request=request)
    except ImportError:
        pass
    return jobs, job_content


def newsletter_events_list(request, start_dt, end_dt, simplified):
    events = []
    event_content = u''
    try:
        from tendenci.apps.events.models import Event

        events = Event.objects.filter(
            start_dt__gt=start_dt,
            start_dt__lt=end_dt,
            status_detail='active',
            status=True,
            allow_anonymous_view=True).order_by('start_dt')

        event_content = render_to_string(
            template_name='newsletters/events_list.txt', context={
            'events': events,
            'start_dt': start_dt,
            'end_dt': end_dt,
            'simplified':simplified},
            request=request)

    except ImportError:
        pass
    return events, event_content


def newsletter_directories_list(request, directories_days, simplified):
    directories = []
    directories_content = ''
    try:
        from tendenci.apps.directories.models import Directory
        end_dt = datetime.datetime.now()
        start_dt = get_start_dt(directories_days, end_dt)

        directories = Directory.objects.filter(activation_dt__lte=end_dt)
        if start_dt:
            directories = directories.filter(activation_dt__gt=start_dt)
        directories = directories.filter(status_detail='active', status=True, allow_anonymous_view=True)
        directories = directories.order_by('status_detail','list_type','-activation_dt')
        directories_content = render_to_string(template_name='newsletters/directories_list.txt',
                                       context={'directories': directories,
                                        'start_dt': start_dt,
                                        'end_dt': end_dt,
                                        'simplified':simplified},
                                       request=request)
    except ImportError:
        pass
    return directories, directories_content


def newsletter_resumes_list(request, resumes_days, simplified):
    resumes = []
    resumes_content = ''
    try:
        from tendenci.apps.resumes.models import Resume
        end_dt = datetime.datetime.now()
        start_dt = get_start_dt(resumes_days, end_dt)

        resumes = Resume.objects.filter(activation_dt__lte=end_dt)
        if start_dt:
            resumes = resumes.filter(activation_dt__gt=start_dt)
        resumes = resumes.filter(status_detail='active', status=True, allow_anonymous_view=True)
        resumes = resumes.order_by('status_detail','list_type','-activation_dt')
        resumes_content = render_to_string(template_name='newsletters/resumes_list.txt',
                                       context={'resumes': resumes,
                                        'start_dt': start_dt,
                                        'end_dt': end_dt,
                                        'simplified':simplified},
                                       request=request)
    except ImportError:
        pass
    return resumes, resumes_content


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
    content = str(template.html_file.file.read(), "utf-8")
    pattern = r'"[^"]*?\.(?:(?i)jpg|(?i)jpeg|(?i)png|(?i)gif|(?i)bmp|(?i)tif|(?i)css)"'

    def repl(x):
        return '"%s/%s/%s"' % (
            site_url,
            template.get_media_url(),
            x.group(0).replace('"', ''))

    new_content = re.sub(pattern, repl, content)
    return new_content
