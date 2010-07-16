from datetime import datetime
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
from event_logs.models import EventLog, EventLogBaseColor, EventLogColor
from event_logs.utils import day_bars, month_days,\
    request_month_range
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from base.http import Http403
from forms import EventsFilterForm


def index(request, id=None, template_name="event_logs/view.html"):
    if not id: return HttpResponseRedirect(reverse('event_log.search'))
    event_log = get_object_or_404(EventLog, pk=id)

    if request.user.has_perm('event_logs.view_eventlog'):
        return render_to_response(template_name, {'event_log': event_log}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="event_logs/search.html"):
    if not request.user.has_perm('event_logs.view_eventlog'): raise Http403
    
    event_logs = EventLog.objects.search(request.GET)
        
    return render_to_response(template_name, {'event_logs':event_logs}, 
        context_instance=RequestContext(request))

def print_view(request, id, template_name="event_logs/print-view.html"):
    event_log = get_object_or_404(EventLog, pk=id)
     
    if request.user.has_perm('event_logs.view_eventlog'):
        return render_to_response(template_name, {'event_log': event_log}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
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


def source_colors(data):
    for item in data:
        item['color'] = EventLogBaseColor.get_color(item['source'])

def event_colors(data):
    for item in data:
        item['color'] = EventLogColor.get_color(item['event_id'])

@staff_member_required
def event_summary_report(request):
    queryset = EventLog.objects.all()
    form = EventsFilterForm(request.GET)
    if form.is_valid():
        queryset = form.process_filter(queryset)
    
    from_date, to_date = request_month_range(request)
    queryset = queryset.filter(create_dt__gte=from_date, create_dt__lte=to_date)
    
    chart_data = queryset\
                .extra(select={'day':'DATE(create_dt)'})\
                .values('day', 'source')\
                .annotate(count=Count('pk'))\
                .order_by('day', 'source')
    chart_data = day_bars(chart_data, from_date.year, from_date.month, 300, source_colors)
    
    summary_data = queryset\
                .values('source')\
                .annotate(count=Count('pk'))\
                .order_by('source')
    source_colors(summary_data)

    return render_to_response(
                'reports/event_summary.html', 
                {'chart_data': chart_data, 'summary_data':summary_data, 
                 'form': form, 'date_range': (from_date, to_date)},  
                context_instance=RequestContext(request))

@staff_member_required
def event_source_summary_report(request, source):
    queryset = EventLog.objects.filter(source=source)
    form = EventsFilterForm(request.GET)
    if form.is_valid():
        queryset = form.process_filter(queryset)
    
    from_date, to_date = request_month_range(request)
    queryset = queryset.filter(create_dt__gte=from_date, create_dt__lte=to_date)
    
    chart_data = queryset\
                .extra(select={'day':'DATE(create_dt)'})\
                .values('day', 'event_id')\
                .annotate(count=Count('pk'))\
                .order_by('day', 'event_id')
    chart_data = day_bars(chart_data, from_date.year, from_date.month, 300, event_colors)
    
    summary_data = queryset\
                .values('event_id')\
                .annotate(count=Count('pk'))\
                .order_by('event_id')
    event_colors(summary_data)
    
    return render_to_response(
                'reports/event_source_summary.html', 
                {'chart_data': chart_data, 'summary_data':summary_data, 
                 'form': form, 'date_range': (from_date, to_date),
                 'source':source},  
                context_instance=RequestContext(request))
    