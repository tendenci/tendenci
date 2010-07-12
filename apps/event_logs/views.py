from os.path import join, isdir
from os import mkdir
from PIL import Image

from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings

from base.http import render_to_403
from event_logs.models import EventLog
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required

@permission_required('event_logs.view_eventlog')
def index(request, id=None, template_name="event_logs/view.html"):
    if not id: return HttpResponseRedirect(reverse('event_log.search'))
    event_log = get_object_or_404(EventLog, pk=id)

    if request.user.has_perm('event_logs.view_eventlog', event_log):
        return render_to_response(template_name, {'event_log': event_log}, 
            context_instance=RequestContext(request))
    else:
        return render_to_403()

@permission_required('event_logs.view_eventlog')
def search(request, template_name="event_logs/search.html"):
    event_logs = EventLog.objects.search(request.GET)
        
    return render_to_response(template_name, {'event_logs':event_logs}, 
        context_instance=RequestContext(request))

@permission_required('event_logs.view_eventlog')
def print_view(request, id, template_name="event_logs/print-view.html"):
    event_log = get_object_or_404(EventLog, pk=id)
     
    if request.user.has_perm('articles.view_article', event_log):
        return render_to_response(template_name, {'event_log': event_log}, 
            context_instance=RequestContext(request))
    else:
        return render_to_403()
    
@login_required
def colored_image(request, color):
    from webcolors import hex_to_rgb
    
    base_dir = join(settings.MEDIA_ROOT,'event_logs')
    full_path = join(base_dir,'%s.png' % color)
    
    # make the dir if it doesn't exist
    if not isdir(base_dir):
        mkdir(base_dir)
        
    try:
        f = open(full_path,'rb')
        data = f.read()
        f.close()
    except:
        rgb = hex_to_rgb('#%s' % color)
        image = Image.new('RGB',(1,1),rgb)
        image.save(full_path,"PNG")
        f = open(full_path,'rb')
        data = f.read()
        f.close()

    return HttpResponse(data, mimetype="image/png")

@staff_member_required
def event_summary_report(request):
    items = EventLog.objects.all()\
                .extra(select={'day':'DATE(create_dt)'})\
                .values('day', 'source')\
                .annotate(count=Count('pk'))\
                .order_by('day', 'source')
    data = dict([(i, []) for i in range(1,32)])
    
    for item in items:
        print item
    return render_to_response(
                'reports/event_summary.html', 
                {'items': items},  
                context_instance=RequestContext(request))
