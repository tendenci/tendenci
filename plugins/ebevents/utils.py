from os.path import join
import urllib2
from datetime import datetime
from BeautifulSoup import BeautifulStoneSoup

from django.conf import settings
from django.core.cache import cache
from django.utils.html import strip_tags

DEFAULT_URL = 'http://go.eventbooking.com/xml_public.asp?pwl=4E1.5B2115DE'
EVENTBOOKING_XML_URL = getattr(settings, 'EVENTBOOKING_XML_URL', DEFAULT_URL)

# Code when eventbooking goes down
# EVENTBOOKING_XML_PATH =  join(settings.MEDIA_ROOT, 'ebevents')

def get_event_by_id(id, **kwargs):
    event = {}
    keys = [settings.CACHE_PRE_KEY, 'event_booking_event_detail_%s' % id]
    cache_key = '.'.join(keys)
    xml_url = '%s&mode=detail&event_id=%s' % (EVENTBOOKING_XML_URL, id)

    # pull from cache
    xml = cache.get(cache_key)

    # cache if not already cached
    if not xml:
        #event_xml_path = join(EVENTBOOKING_XML_PATH, 'event_%s.xml' % id)
        #with open(event_xml_path, 'r') as f:
        #    xml = f.read()
        url_object = urllib2.urlopen(xml_url, timeout=120)
        xml = url_object.read()

        # cache the content for one hour
        cache.set(cache_key, xml, 60*60*2)
    
    soup = BeautifulStoneSoup(xml)
    node = soup.find('public_event_detail')
    
    try:
        event['event_name'] = node.event_name.string
    except AttributeError:
        return None
        
    event['event_name'] = strip_tags(event['event_name'])
    event['event_type'] = strip_tags(node.event_type.string)
    event['unique_event_id'] = node.unique_event_id.string
    
    # date time
    try:
        start_date = node.showtimes.subevent['startdate']
        start_date = datetime.strptime(start_date, '%Y-%b-%d')
    except:
        start_date = ''
    try:
        start_time = node.showtimes.subevent['starttime']
        start_time =  datetime.strptime(start_time.strip(), '%I:%M:%S %p')
        #start_time = start_time.replace(":00 ", " ")   # 04:00:00 PM - fix later by converting to dt
    except:
        start_time = ''

        
    try:
        end_date = node.showtimes.subevent['enddate']
        end_date = datetime.strptime(end_date, '%Y-%b-%d')
    except:
        end_date = ''
    try:
        end_time = node.showtimes.subevent['endtime']
        end_time =  datetime.strptime(end_time.strip(), '%I:%M:%S %p')
    except:
        end_time = ''
     
    if not start_date:
        start_date = node.date_range.start_date.string
        start_date = datetime.strptime(start_date, '%Y-%b-%d')
        start_time = node.date_range.start_time.string
        try:
            start_time =  datetime.strptime(start_time.strip(), '%I:%M:%S %p')
        except:
            pass 
        end_date = node.date_range.end_date.string
        end_date = datetime.strptime(end_date, '%Y-%b-%d')
        end_time = node.date_range.end_time.string
        try:
            end_time =  datetime.strptime(end_time.strip(), '%I:%M:%S %p')
        except:
            pass 
           
    event['start_date'] = start_date
    event['start_time'] = start_time
    event['end_date'] = end_date
    event['end_time'] = end_time
    
    # description
    try:
        event['description'] = node.description.string
    except:
        event['description'] = ''
    if event['description']:
        event['description'] = event['description'].replace('&amp;', '&').replace('&apos;', "'")
        event['description'] = event['description'].replace('&lt;', '<')
        event['description'] = event['description'].replace('&gt;', '>')
    
    # caption
    try:
        event['caption'] = node.subevents.subevent['caption'] 
    except:
        event['caption'] = ""
    
    # ticket
    event['ticket_info'] = node.ticket_info.string
    if event['ticket_info']:
        event['ticket_info'] = event['ticket_info'].replace('&amp;', '&').replace('&apos;', "'")
        event['ticket_info'] = event['ticket_info'].replace('&lt;', '<')
        event['ticket_info'] = event['ticket_info'].replace('&gt;', '>')
        event['ticket_info'] = event['ticket_info'].replace('&quot;', "'")
   
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

    # was commented out, needed for ICS generation, defaulted to false
    event['venue_website'] = ''
    
    # additional info
    event['additional_info'] = node.additional_info.string
    event['additional_info'] = strip_tags(event['additional_info'])
    
    # additional info 2
    try:
        event['additional_info2'] = node.additional_info2.string
        event['additional_info2'] = strip_tags(event['additional_info2'])
    except:
        event['additional_info2'] = ''
    
    # picture full
    # Removed 6/6/2011 at request of client in favor of special media photos
    #event['picture_full'] = ''
    #if node.picture_full:
    #    event['picture_full'] = node.picture_full.string
    #    event['picture_full_height'] = int(node.picture_full['height'])
    #    event['picture_full_width'] = int(node.picture_full['width'])
    
    # special media photo fields        
    if node.media_group:
        for media in node.media_group:
            label = media['type'].lower()
            try:
                event[label] = media.string
                event[label + '_height'] = int(media['height'])
                event[label + '_width'] = int(media['width'])
            except:
                event[label] = ''
                event[label + '_height'] = ''
                event[label + '_width'] = ''
    
    # weird - those elements appear as upper case in the xml file
    # but the parser only takes as lower case. Need to change all to lower case
    elements = ['DIRURL', 'TI', 'MI', 'SEATCHART', 'RM', 'SPONS',
                'PARKING', 'PROMOTER', 'PRESENTER', 'PRODUCER', 
                'OPENING_ACT', 'CONTACT', 'SPECIAL_ENT', 'DOORSOPEN',
                'RESTR', 'CONTACT_PHONE', 'CONTACT_EMAIL', 'VIDEO', 
                'AUDIO', 'GROUPSALES']
    elements = [e.lower() for e in elements]
    
    for e in elements:
        try:
            event[e] = (getattr(node, e)).string
            event[e + '_caption'] = (getattr(node, e))['caption']
        except:
            event[e]= ''
            event[e + '_caption'] = ''
            
    if event['rm']:
        node_rm = node.rm
        while node_rm.nextSibling.name == 'rm':
            event['rm'] = '%s <br> %s' % (event['rm'], node_rm.nextSibling.string)
            node_rm = node.rm.nextSibling
            
    return event


def build_ical_text(event, d):
    ical_text = '%s\n\n' % d['event_url']
    
    # title
    ical_text += "Event Name: %s\n" % strip_tags(event['event_name'])
    
    # start_dt
    if event['start_dt']:
        ical_text += 'Start Date / Time: %s CST\n' % (event['start_dt'].strftime('%b %d, %Y %I:%M %p'))
    
    # location
    if event['location']:
        ical_text += 'Location: %s\n' % (event['location'])
    if event['venue_name']:
        ical_text += 'Venue: %s\n' % (event['venue_name'])
    if event['venue_website']:
        ical_text += '%s\n' % (event['venue_website'])
            
    ical_text += strip_tags(event['description'])
    
    ical_text  = ical_text.replace(';', '\;')
    ical_text  = ical_text.replace('\n', '\\n')
   
    return ical_text
    
def build_ical_html(event, d):  
    # title
    ical_html = "<h1>Event Name: %s</h1>" % (event['event_name'])
    
    ical_html += '<div>%s</div><br />' % d['event_url']
    
    # start_dt
    if event['start_dt']:
        ical_html += '<div>When: %s CST</div>' % (event['start_dt'].strftime('%b %d, %Y %I:%M %p')) 
        
    # location
    if event['location']:
        ical_html += '<div>Location: %s</div>' % (event['location'])
    if event['venue_name']:
        ical_html += '<div>Venue: %s</div>' % (event['venue_name'])
    if event['venue_website']:
        ical_html += '<div>%s</div>' % (event['venue_website'])
   
    ical_html += '<div>%s</div>' % (event['description'])
    
    ical_html  = ical_html.replace(';', '\;')
    #ical_html  = degrade_tags(ical_html.replace(';', '\;'))
   
    return ical_html
