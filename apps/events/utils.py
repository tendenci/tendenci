import re
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags
from site_settings.utils import get_setting

def get_vevents(request, d):
    from django.conf import settings
    from timezones.utils import adjust_datetime_to_timezone
    from events.models import Event
    
    site_url = get_setting('site', 'global', 'siteurl')
    
    e_str = ""
    events = Event.objects.search(None, user=request.user)
    for evnt in events:
        event = evnt.object
        e_str += "BEGIN:VEVENT\n"
        
        # organizer
        organizers = event.organizer_set.all()
        if len(organizers) > 0:
            organizer = organizers[0]
            if organizer.user:
                e_str += "ORGANIZER:MAILTO:%s\n" % (organizer.user.email)
        
        # date time 
        if event.start_dt:
            start_dt = adjust_datetime_to_timezone(event.start_dt, settings.TIME_ZONE, 'GMT')
            start_dt = start_dt.strftime('%Y%m%dT%H%M%SZ')
            e_str += "DTSTART:%s\n" % (start_dt)
        if event.end_dt:
            end_dt = adjust_datetime_to_timezone(event.end_dt, settings.TIME_ZONE, 'GMT')
            end_dt = end_dt.strftime('%Y%m%dT%H%M%SZ')
            e_str += "DTEND:%s\n" % (end_dt)
        
        # location
        if event.place:
            e_str += "LOCATION:%s\n" % (event.place.name)
            
        e_str += "TRANSP:OPAQUE\n"
        e_str += "SEQUENCE:0\n"
        
        # uid
        e_str += "UID:uid%d@%s\n" % (event.pk, d['domain_name'])
        
        event_url = "%s%s" % (site_url, reverse('event', args=[event.pk]))
        d['event_url'] = event_url
        
        # text description
        e_str += "DESCRIPTION:%s\n" % (build_ical_text(event,d))
        #  html description
        e_str += "X-ALT-DESC;FMTTYPE=text/html:%s\n" % (build_ical_html(event,d))
        
        e_str += "SUMMARY:%s\n" % strip_tags(event.title)
        e_str += "PRIORITY:5\n"
        e_str += "CLASS:PUBLIC\n"
        e_str += "BEGIN:VALARM\n"
        e_str += "TRIGGER:-PT30M\n"
        e_str += "ACTION:DISPLAY\n"
        e_str += "DESCRIPTION:Reminder\n"
        e_str += "END:VALARM\n"
        e_str += "END:VEVENT\n"
        
    return e_str

def build_ical_text(event, d):
    ical_text = "--- This iCal file does *NOT* confirm registration.\n"
    ical_text += "Event details subject to change. ---\n"
    ical_text += '%s\n\n' % d['event_url']
    
    # title
    ical_text += "Event Title: %s\n" % strip_tags(event.title)
    
    # start_dt
    ical_text += 'Start Date / Time: %s %s\n' % (event.start_dt.strftime('%b %d, %Y %H:%M %p'), event.timezone)
    
    # location
    ical_text += 'Event Location: %s\n' % (event.place.name)
    
    # sponsor
    ical_text += 'Event Sponsor: %s\n' % ('')
    
    # speaker
    speakers = event.speaker_set.all()
    if speakers:
        speaker_name_list = [speaker.name for speaker in speakers]
        ical_text += 'Event Speaker: %s\n' % (', '.join(speaker_name_list))
        
    # maps
    show_map_link = False
    if (event.place.address and event.place.city and event.place.state) \
                or (event.place.address and event.place.zip):
        show_map_link = True
    if show_map_link:
        ical_text += "Google\n"
        ical_text += "http://maps.google.com/maps?q="
        ical_text += event.place.address.replace(" ", "+")
        if event.place.city:
            ical_text += ','
            ical_text += event.place.city
        if event.place.state:
            ical_text += ','
            ical_text += event.place.state
        if event.place.zip:
            ical_text += ','
            ical_text += event.place.zip
            
        ical_text += "\n\nForecast\n"
        ical_text += "http://www.weather.com/weather/monthly/%s\n\n" % (event.place.zip)
            
    ical_text += strip_tags(event.description)
    
    ical_text += "--- This iCal file does *NOT* confirm registration."
    ical_text += "Event details subject to change. ---\n\n"
    ical_text += "--- Tendenci(tm) Software by Schipul.com - 'The Web Marketing Company' ---\n"
    
    ical_text  = ical_text.replace(';', '\;')
    ical_text  = ical_text.replace('\n', '\\n')
   
    return ical_text
    
def build_ical_html(event, d):
    # disclaimer: registration
    ical_html = "<div>--- This iCal file does *NOT* confirm registration."
    ical_html += "Event details subject to change. ---</div><br />"
    
    # title
    ical_html += "<h1>Event Title: %s</h1>" % (event.title)
    
    ical_html += '<div>%s</div><br />' % d['event_url']
    
    # start_dt
    ical_html += '<div>When: %s %s</div>' % (event.start_dt.strftime('%b %d, %Y %H:%M %p'), event.timezone)
    
    # sponsor
    ical_html += '<div>Sponsor: %s</div>' % ('')
    
    # speaker
    speakers = event.speaker_set.all()
    if speakers:
        speaker_name_list = [speaker.name for speaker in speakers]
        ical_html += '<div>Event Speaker: %s</div>' % (', '.join(speaker_name_list))
        
    ical_html += '<br />'
    
    # maps
    show_map_link = False
    if (event.place.address and event.place.city and event.place.state) \
                or (event.place.address and event.place.zip):
        show_map_link = True
    if show_map_link:
        # location
        ical_html += '%s<br />' % (event.place.name)
        ical_html += '%s<br />' % (event.place.address)
        if event.place.city and event.place.state:
            ical_html += '%s, %s' % (event.place.city, event.place.state)
        if event.place.zip:
            ical_html += ' %s' % (event.place.zip)
        ical_html += '<br />'
    
        ical_html += "<div>"
        ical_html += "http://maps.google.com/maps?q="
        ical_html += event.place.address.replace(" ", "+")
        if event.place.city:
            ical_html += ','
            ical_html += event.place.city
        if event.place.state:
            ical_html += ','
            ical_html += event.place.state
        if event.place.zip:
            ical_html += ','
            ical_html += event.place.zip
        ical_html += "</div><br />"
            
        ical_html += "<div>Forecast: "
        ical_html += "http://www.weather.com/weather/monthly/%s</div><br /><br />" % (event.place.zip)
            
    ical_html += '<div>%s</div>' % (event.description)
    
    ical_html += "<div>--- This iCal file does *NOT* confirm registration."
    ical_html += "Event details subject to change. ---</div>"
    ical_html += "<div>--- Tendenci(tm) Software by Schipul.com - 'The Web Marketing Company' ---</div>"
    
    #ical_html  = ical_html.replace(';', '\;')
    ical_html  = degrade_tags(ical_html.replace(';', '\;'))
   
    return ical_html

# degrade header tags h1, h2..., h6 to font tags for MS outlook
def degrade_tags(str):
    # h1 --> font size 6
    str = re.sub(r'<h1[^>]*>(.+)</h1>', r'<div><strong><font size="6">\1</font></strong></div>', str)
    
    # h2 --> font size 5
    str = re.sub(r'<h2[^>]*>(.+)</h2>', r'<div><strong><font size="5">\1</font></strong></div>', str)
    
    # h3 --> font size 4
    str = re.sub(r'<h3[^>]*>(.+)</h3>', r'<div><strong><font size="4">\1</font></strong></div>', str)
    
    # h4 --> font size 3
    str = re.sub(r'<h4[^>]*>(.+)</h4>', r'<div><strong><font size="3">\1</font></strong></div>', str)
    
    # h5 --> font size 2
    str = re.sub(r'<h5[^>]*>(.+)</h5>', r'<div><strong><font size="2">\1</font></strong></div>', str)
    
    # h6 --> font size 1
    str = re.sub(r'<h6[^>]*>(.+)</h6>', r'<div><strong><font size="1">\1</font></strong></div>', str)
    print str
    return str
      

def next_month(month, year):
    # TODO: cleaner way to get next date
    next_month = (month+1)%13
    next_year = year
    if next_month == 0:
        next_month = 1
        next_year += 1

    return (next_month, next_year)

def prev_month(month, year):
    # TODO: cleaner way to get previous date
    prev_month = (month-1)%13
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    return (prev_month, prev_year)

def save_registration(*args, **kwargs):
    """
    Adds or Updates Registration Record.
    """
    from events.models import Registration

    event = kwargs.get('event', None)
    user_account = kwargs.get('user', None)
    payment_method = kwargs.get('payment_method', None)
    price = kwargs.get('price', None)

    # user profile shortcut
    user_profile = user_account.get_profile()

    try: # update registration
        reg8n = Registration.objects.get(
            event=event, creator=user_account, owner=user_account,
            payment_method=payment_method, amount_paid=price
        )
        created = False

    except: # add registration
        reg8n = Registration.objects.create(
            event = event, 
            creator = user_account, 
            owner = user_account,
            payment_method_id = payment_method.pk,
            amount_paid = str(price)
        )
        created = True

    # get or create registrant
    registrant = reg8n.registrant_set.get_or_create(user=user_account)[0]

    # update registrant information                
    registrant.name = ' '.join((user_account.first_name, user_account.last_name))
    registrant.name = registrant.name.strip()
    registrant.mail_name = user_profile.display_name
    registrant.address = user_profile.address
    registrant.city = user_profile.city
    registrant.state = user_profile.state
    registrant.zip = user_profile.zipcode
    registrant.country = user_profile.country
    registrant.phone = user_profile.phone
    registrant.email = user_profile.email
    registrant.company_name = user_profile.company
    registrant.position_title = user_profile.position_title
    registrant.save()

    reg8n.save() # save registration record
    reg8n.save_invoice() # adds/updates invoice

    # TODO: Debating on whether I should pass
    # the invoice object as well

    return (reg8n, created)





