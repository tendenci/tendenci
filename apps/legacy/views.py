from django.http import HttpResponsePermanentRedirect, Http404
from django.core.urlresolvers import reverse
from django.db import connection, transaction

def redirect(request, content_type, id=0, qs=None, *args, **kwargs):
    cursor = connection.cursor()
    
    ids =[]
    items = request.GET.items()
    for i in items:
        try:
            ids.append(int(i[0]))    
        except:
            pass
            
        try:
            ids.append(int(i[1]))    
        except:
            pass
    
    if ids:
        id = ids[0]        
    
    if content_type == "articles":
        try:
            cursor.execute("SELECT slug FROM mig_articles_article_t4_to_t5 as mig JOIN articles_article as art on art.id = mig.t5_id WHERE t4_id = %s", [id])
            t5_slug = cursor.fetchone()
            t5_slug = str(t5_slug[0])
        except:
            raise Http404
        return HttpResponsePermanentRedirect(reverse('article', args=[t5_slug]))
    
    if content_type == "events":
        try:
            cursor.execute("SELECT t5_id FROM mig_events_event_t4_to_t5 WHERE t4_id = %s", [id])
            t5_id = cursor.fetchone()
            t5_id = int(t5_id[0])
        except:
            raise Http404
        return HttpResponsePermanentRedirect(reverse('event', args=[t5_id]))
        
    if content_type == "help_files":
        try:
            cursor.execute("SELECT slug FROM mig_help_files_helpfile_t4_to_t5 as mig JOIN help_files_helpfile as hf on hf.id = mig.t5_id WHERE t4_id = %s", [id])
            t5_slug = cursor.fetchone()
            t5_slug = str(t5_slug[0])
        except:
            raise Http404
        return HttpResponsePermanentRedirect(reverse('help_file.details', args=[t5_slug]))
        
    if content_type == "news":
        try:
            cursor.execute("SELECT slug FROM mig_news_news_t4_to_t5 as mig JOIN news_news as nw on nw.id = mig.t5_id WHERE t4_id = %s", [id])
            t5_slug = cursor.fetchone()
            t5_slug = str(t5_slug[0])
        except:
            raise Http404
        return HttpResponsePermanentRedirect(reverse('news.view', args=[t5_slug]))
        
    if content_type == "pages":
        try:
            cursor.execute("SELECT slug FROM mig_pages_page_t4_to_t5 as mig JOIN pages_page as pg on pg.id = mig.t5_id WHERE t4_id = %s", [id])
            t5_slug = cursor.fetchone()
            t5_slug = str(t5_slug[0])
        except:
            raise Http404
        return HttpResponsePermanentRedirect(reverse('page', args=[t5_slug]))
        
    if content_type == "photo_sets":
        try:
            cursor.execute("SELECT t5_id FROM mig_photos_photoset_t4_to_t5 WHERE t4_id = %s", [id])
            t5_id = cursor.fetchone()
            t5_id = int(t5_id[0])
        except:
            raise Http404
        return HttpResponsePermanentRedirect(reverse('photoset_details', args=[t5_id]))
        
    if content_type == "photos":
        try:
            cursor.execute( "SELECT t5_id FROM mig_photos_image_t4_to_t5 WHERE t4_id = %s", [id])
            t5_id = cursor.fetchone()
            t5_id = int(t5_id[0])
        except:
            raise Http404
        return HttpResponsePermanentRedirect(reverse('photo_details', args=[t5_id]))
