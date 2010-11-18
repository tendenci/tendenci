import os
import urllib2
from datetime import datetime
import time
import cPickle
from BeautifulSoup import BeautifulStoneSoup
from django.template import RequestContext
#from django.core.urlresolvers import reverse
#from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings

#from site_settings.utils import get_setting
from base.http import Http403
from forms import EventSearchForm

def list(request, form_class=EventSearchForm, template_name="ebevents/list.html"):
    q_event_month = request.GET.get('event_month', '')
    q_event_year = request.GET.get('event_year', '')
    q_event_type = request.GET.get('event_type', '')
    
    try:
        q_event_month = int(q_event_month)
    except:
        q_event_month = 0
    try:
        q_event_year = int(q_event_year)
    except:
        q_event_year = 0    
    
    # check the cache first
    cache_file_name = 'events.txt'
    cache_path = os.path.join(settings.MEDIA_ROOT, 'ebevents/')
    
    use_cache = False
    
    if not os.path.isdir(cache_path):
        os.mkdir(cache_path)
    cache_path = os.path.join(cache_path, cache_file_name)
    
    if os.path.isfile(cache_path):
        if time.time() - os.path.getmtime(cache_path) < 3600: # 1 hour
            use_cache = True
       
    if use_cache: 
        fd = open(cache_path, 'r')
        content = fd.read()
        fd.close()
        
        events = cPickle.loads(content)
    else:
        # process all events and store in the cache
        try:
            xml_path = settings.EVENTBOOKING_XML_URL
        except:
            xml_path = "http://xml.eventbooking.com/xml_public.asp?pwl=4E2.4AA4404E"
            
        xml = urllib2.urlopen(xml_path)
        soup = BeautifulStoneSoup(xml)
        
        events = []
        nodes = soup.findAll('event')
        for node in nodes:
            event_type = node.event_type.string
            event_type = event_type.replace('&amp;', '&')
            #if event_type <> u'HPL Express Events':
            start_date = node.date_range.start_date.string
            if start_date:
                #start_date = (datetime.strptime(start_date, '%Y-%b-%d')).strftime('%m/%d/%Y')
                start_date = datetime.strptime(start_date, '%Y-%b-%d')
            
            events.append({'event_name': node.event_name.string, 
                           'event_type': event_type,
                           'start_date': start_date,
                           'unique_event_id':node.unique_event_id.string})
        flat_events = cPickle.dumps(events)
        fd = open(cache_path, 'w')
        fd.write(flat_events)
        fd.close()
        
    # make event type list
    event_types = set([evnt['event_type'] for evnt in events])
    event_types = [t for t in event_types]
    event_types.sort()
   
    
    # make year list
    event_years = set([evnt['start_date'].year for evnt in events if evnt['start_date']])
     
    # filter type  
    if q_event_type <> "":
        events = [event for event in events if event['event_type']==q_event_type]
    
    # filter date  
    if q_event_month and q_event_year:
        events = [event for event in events if event['start_date'].year==q_event_year and \
                  event['start_date'].month==q_event_month]
    elif q_event_month:
        events = [event for event in events if event['start_date'].month==q_event_month]
    elif q_event_year:
        events = [event for event in events if event['start_date'].year==q_event_year]
        

    # set form initials and choices    
    form = form_class()
    form.fields['event_month'].initial = q_event_month
    
    form.fields['event_year'].initial = q_event_year
    form.fields['event_year'].choices = [("", "Select Year")] + [(year, year) for year in event_years]
    
    form.fields['event_type'].initial = q_event_type
    form.fields['event_type'].choices = [("", "Select Category")] + [(e_type, e_type) for e_type in event_types]
    
  
    return render_to_response(template_name, {'form': form,
                                              'events': events, 
                                              'event_types': event_types,
                                              'selected_event_type':q_event_type}, 
        context_instance=RequestContext(request))
    
def display(request, id, template_name="ebevents/display.html"):
    if not id: raise Http403
        
    try:
        xml_url = settings.EVENTBOOKING_XML_URL
    except:
        xml_url = "http://xml.eventbooking.com/xml_public.asp?pwl=4E2.4AA4404E"
        
    xml_url = '%s&mode=detail&event_id=%s' % (xml_url.strip(), id)
        
    xml = urllib2.urlopen(xml_url)
    soup = BeautifulStoneSoup(xml)
    node = soup.find('public_event_detail')
    
    event = {}
    
    event['event_name'] = node.event_name.string
    event['event_type'] = node.event_type.string
    event['unique_event_id'] = node.unique_event_id.string
    
    # date time
    try:
        start_date = node.showtimes.subevent['startdate']
        start_date = datetime.strptime(start_date, '%Y-%b-%d')
    except:
        start_date = ''
    try:
        start_time = node.showtimes.subevent['starttime']
        start_time = start_time.replace(":00 ", " ")   # 04:00:00 PM - fix later by converting to dt
    except:
        start_time = ''
        
    try:
        end_date = node.showtimes.subevent['enddate']
        end_date = datetime.strptime(end_date, '%Y-%b-%d')
    except:
        end_date = ''
    try:
        end_time = node.showtimes.subevent.string
        end_time = end_time.replace('-', '')
    except:
        end_time = ''
     
    if not start_date:
        start_date = node.date_range.start_date.string
        start_date = datetime.strptime(start_date, '%Y-%b-%d')
        start_time = node.date_range.start_time.string
        end_date = node.date_range.end_date.string
        end_date = datetime.strptime(end_date, '%Y-%b-%d')
        end_time = node.date_range.end_time.string
           
    event['start_date'] = start_date
    event['start_time'] = start_time
    event['end_date'] = end_date
    event['end_time'] = end_time
    
    print event['start_time']
    print event['end_time']
    
    # description
    event['description'] = node.description.string
    event['description'] = event['description'].replace('&amp;', '&')
    #event['description'] = event['description'].replace('&lt;', '<')
    #event['description'] = event['description'].replace('&gt;', '>')
    # caption
    try:
        event['caption'] = node.subevents.subevent['caption'] 
    except:
        event['caption'] = ""
    
    # ticket
    event['ticket_info'] = node.ticket_info.string
    event['ticket_prices'] = node.ticket_prices.string
    event['ticket_sale_date'] = node.ticket_sale_date.string
    try:
        event['ticket_sale_date'] = datetime.strptime(event['ticket_sale_date'], '%Y-%b-%d')
    except:
        pass
    event['ticket_sale_time'] = node.ticket_sale_time.string
    
    # location
    event['location'] = node.location.string
    event['venue_name'] = node.venue_name.string
    event['venue_website'] = node.venue_website.string
    
    # additional info
    event['additional_info'] = node.additional_info.string
    
    # picture thumb
    event['picture_thumb'] = node.picture_thumb.string
    if event['picture_thumb']:
        event['picture_thumb_height'] = int(node.picture_thumb['height'])
        event['picture_thumb_width'] = int(node.picture_thumb['width'])
    
    # picture full
    event['picture_full'] = node.picture_full.string
    if event['picture_full']:
        event['picture_full_height'] = int(node.picture_full['height'])
        event['picture_full_width'] = int(node.picture_full['width'])
    
    # weird - those elements appear as upper case in the xml file
    # but the parser only takes as lower case. Need to change all to lower case
    elements = ['DIRURL', 'TI', 'MI', 'SEATCHART', 'RM', 'SPONS',
                'PARKING', 'PROMOTER', 'PRESENTER', 'PRODUCER', 
                'OPENING_ACT', 'CONTACT', 'SPECIAL_ENT', 'DOORSOPEN',
                'RESTR', 'CONTACT_PHONE', 'CONTACT_EMAIL', 'VIDEO', 
                'AUDIO', 'GROUPSALES']
    elements = [e.lower() for e in elements]
    
    for e in elements:
        print e
        try:
            event[e] = eval("node.%s.string" % e) 
            event[e + '_caption'] = eval("node.%s['caption']" %e)
        except:
            event[e]= ''
            event[e + '_caption'] = ''
    
    return render_to_response(template_name, {'event': event}, 
        context_instance=RequestContext(request))
    
    
    
