import datetime
from django.template.loader import render_to_string
from django.template import RequestContext

def newsletter_articles_list(request, articles_days, simplified):
    from articles.models import Article
    end_dt = datetime.datetime.now()
    try:
        articles_days = int(articles_days)
    except:
        articles_days = 0
    if articles_days > 0:
        start_dt = end_dt - datetime.timedelta(days=articles_days)
    else:
        start_dt = None
    articles = Article.objects.filter(release_dt__lte=end_dt)
    if start_dt:
        articles = articles.filter(release_dt__gt=start_dt)
    articles = articles.filter(status_detail='active', status=1)
    articles = articles.order_by("-release_dt")
    art_content = render_to_string('newsletters/articles_list.txt', 
                                   {'articles': articles,
                                    'start_dt': start_dt,
                                    'end_dt': end_dt,
                                    'simplified':simplified},
                                   context_instance=RequestContext(request))
    
    return art_content