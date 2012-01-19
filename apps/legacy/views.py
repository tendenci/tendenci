from django.http import HttpResponsePermanentRedirect, Http404
from django.core.urlresolvers import reverse
from django.db import connection, transaction


def redirect_for_search(content_type):
    """
    Redirect to an applications search url
    """
    name = ''

    if content_type == 'articles':
        name = 'article.search'
    if content_type == 'events':
        name = 'event.search'
    if content_type == 'help_files':
        name = 'help_files.search'
    if content_type == 'news':
        name = 'news.search'
    if content_type == 'jobs':
        name = 'job.search'
    if content_type == 'pages':
        name = 'page.search'
    if content_type == 'photo_sets':
        name = 'photoset_latest'
    if content_type == 'photos':
        name = 'photoset_latest'
    if content_type == 'quotes':
        name = 'quote.search'
    if content_type == 'attorneys':
        name = 'attorneys'
    if content_type == 'before_and_after':
        name = 'before_and_after.search'
    if content_type == 'products':
        name = 'products.search'

    # app not found
    if not name:
        raise Http404

    return HttpResponsePermanentRedirect(reverse(name))


def redirect_for_view(content_type, id):
    """
    Redirect for hits that are views
    """
    cursor = connection.cursor()
    sql = ''
    redirect_name = ''

    # sql query for each type
    if content_type == 'articles':
        redirect_name = 'article'
        sql = "SELECT slug FROM mig_articles_article_t4_to_t5 as mig " \
              "JOIN articles_article as art on art.id = mig.t5_id "\
              "WHERE t4_id = %s"

    if content_type == 'events':
        redirect_name = 'event'
        sql = "SELECT t5_id FROM mig_events_event_t4_to_t5 WHERE t4_id = %s"

    if content_type == 'help_files':
        redirect_name = 'help_file.details'
        sql = "SELECT slug FROM mig_help_files_helpfile_t4_to_t5 as mig " \
              "JOIN help_files_helpfile as hf on hf.id = mig.t5_id "\
              "WHERE t4_id = %s"

    if content_type == 'news':
        redirect_name = 'news.view'
        sql = "SELECT slug FROM mig_news_news_t4_to_t5 as mig " \
              "JOIN news_news as nw on nw.id = mig.t5_id "\
              "WHERE t4_id = %s"
    
    if content_type == 'jobs':
        redirect_name = 'job'
        sql = "SELECT slug FROM mig_jobs_job_t4_to_t5 as mig " \
              "JOIN jobs_job as j on j.id = mig.t5_id "\
              "WHERE t4_id = %s"

    if content_type == 'pages':
        redirect_name = 'page'
        sql = "SELECT slug FROM mig_pages_page_t4_to_t5 as mig " \
              "JOIN pages_page as pg on pg.id = mig.t5_id " \
              "WHERE t4_id = %s"

    if content_type == 'photo_sets':
        redirect_name = 'photoset_details'
        sql = "SELECT t5_id FROM mig_photos_photoset_t4_to_t5 WHERE t4_id = %s"

    if content_type == 'photos':
        redirect_name = 'photo'
        sql = "SELECT t5_id FROM mig_photos_image_t4_to_t5 WHERE t4_id = %s"

    if content_type == 'quotes':
        redirect_name = 'quote.view'
        sql = "SELECT t5_id FROM mig_quotes_quote_t4_to_t5 WHERE t4_id = %s"

    if content_type == 'attorneys':
        redirect_name = 'attorneys.detail'
        sql = "SELECT slug FROM mig_attorneys_attorney_t4_to_t5 as mig " \
              "JOIN attorneys_attorney as attn on attn.id = mig.t5_id " \
              "WHERE t4_id = %s"

    if content_type == 'before_and_after':
        redirect_name = 'before_and_after.detail'
        sql = "SELECT t5_id FROM mig_before_after_t4_to_t5 as mig " \
              "JOIN before_and_after_beforeandafter as bfa on bfa.id = mig.t5_id " \
              "WHERE t4_id = %s"

    if content_type == 'products':
        redirect_name = 'products.detail'
        sql = "SELECT slug FROM mig_products_t4_to_t5 as mig " \
              "JOIN products_product as prod on prod.id = mig.t5_id " \
              "WHERE t4_id = %s"

    # app not found
    if not sql or not redirect_name:
        raise Http404

    # execute the sql and try to redirect depending on return query
    try:
        cursor.execute(sql, [id])
        redirect_args = cursor.fetchone()[0]
        return HttpResponsePermanentRedirect(reverse(redirect_name, args=[redirect_args]))
    except:
        raise Http404


def redirect(request, content_type=None, view=None, id=None):
    """
    Legacy redirect for T4 to T5 migrated sites
    """
    query_string = request.GET

    # redirect for hits if they don't have
    # an id and a query_string
    if id is None and not query_string:
        return redirect_for_search(content_type)

    # redirect for all search hits with or without query string
    # example /en/articles/search.asp
    if view == 'search':
        return redirect_for_search(content_type)

    # redirect for hits that have an id pattern
    # example /en/articles/v/100 or /en/art/v/100
    if id:
        return redirect_for_view(content_type, id)

    # redirect for a query string in a legacy view page
    # example /en/articles/view.asp?articleid=100
    if query_string and view == 'view':
        id = ''
        for key in query_string.keys():
            if 'id' in key:
                id = query_string[key]
                continue
        if id.isdigit():
            return redirect_for_view(content_type, id)

    # redirect for a query string in a legacy view page
    # example /en/art/?100
    if query_string:
        if len(query_string) == 1:
            if query_string.keys()[0].isdigit():
                id = query_string.keys()[0]
                return redirect_for_view(content_type, id)

    # no criteria matched, 404 them
    raise Http404


def querystring_redirect(request):
    """
    Generic redirect to catch querystrings and redirect to those pages
    """
    query_string = request.GET
    if query_string:
        return HttpResponsePermanentRedirect(query_string.keys()[0])

    raise Http404
