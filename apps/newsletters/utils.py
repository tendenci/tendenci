import datetime
from django.template.loader import render_to_string
from django.template import RequestContext

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
    from articles.models import Article
    end_dt = datetime.datetime.now()
    start_dt = get_start_dt(articles_days, end_dt)
    
    articles = Article.objects.filter(release_dt__lte=end_dt)
    if start_dt:
        articles = articles.filter(release_dt__gt=start_dt)
    articles = articles.filter(status_detail='active', status=True, syndicate=True, allow_anonymous_view=True)
    articles = articles.order_by("-release_dt")
    art_content = render_to_string('newsletters/articles_list.txt', 
                                   {'articles': articles,
                                    'start_dt': start_dt,
                                    'end_dt': end_dt,
                                    'simplified':simplified},
                                   context_instance=RequestContext(request))
    
    return articles, art_content

def newsletter_news_list(request, news_days, simplified):
    from news.models import News
    end_dt = datetime.datetime.now()
    start_dt = get_start_dt(news_days, end_dt)
    
    news = News.objects.filter(release_dt__lte=end_dt)
    if start_dt:
        news = news.filter(release_dt__gt=start_dt)
    news = news.filter(status_detail='active', status=True, syndicate=True, allow_anonymous_view=True)
    news = news.order_by("-release_dt")
    news_content = render_to_string('newsletters/news_list.txt', 
                                   {'news': news,
                                    'start_dt': start_dt,
                                    'end_dt': end_dt,
                                    'simplified':simplified},
                                   context_instance=RequestContext(request))
    
    return news, news_content


def newsletter_pages_list(request, pages_days, simplified):
    from pages.models import Page
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
    
    return pages, page_content


def newsletter_jobs_list(request, jobs_days, simplified):
    from jobs.models import Job
    end_dt = datetime.datetime.now()
    start_dt = get_start_dt(jobs_days, end_dt)
    
    jobs = Job.objects.filter(activation_dt__lte=end_dt)
    if start_dt:
        jobs = jobs.filter(activation_dt__gt=start_dt)
    jobs = jobs.filter(status_detail='active', status=True, syndicate=True, allow_anonymous_view=True)
    jobs = jobs.order_by("list_type")
    job_content = render_to_string('newsletters/jobs_list.txt', 
                                   {'jobs': jobs,
                                    'start_dt': start_dt,
                                    'end_dt': end_dt,
                                    'simplified':simplified},
                                   context_instance=RequestContext(request))
    
    return jobs, job_content
