# NOTE: When updating the registration scheme be sure to check with the
# anonymous registration impementation of events in the registration module.
from builtins import str
import ast
import re
import os.path
import math
import time as ttime
from datetime import datetime, timedelta
from datetime import date
import csv
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY
from decimal import Decimal
import dateutil.parser as dparser

from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.conf import settings
from django.urls import reverse
from django.db import connection
from django.db import models
from django.db.models import Max, Count, Q
from django.template import engines
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
import simplejson
from django.utils.html import strip_tags
from pytz import timezone
from pytz import UnknownTimeZoneError

from tendenci.apps.events.models import (Event, Place, Speaker, Organizer, Sponsor,
    Registration, RegistrationConfiguration, Registrant, RegConfPricing,
    CustomRegForm, Addon, AddonOption, CustomRegField, Type,
    TypeColorSet, RecurringEvent)
from tendenci.apps.discounts.models import Discount, DiscountUse
from tendenci.apps.discounts.utils import assign_discount
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.perms.utils import get_query_filters
from tendenci.apps.imports.utils import extract_from_excel
from tendenci.apps.base.utils import (adjust_datetime_to_timezone,
    format_datetime_range, UnicodeWriter, get_salesforce_access,
    create_salesforce_contact, validate_email)
from tendenci.apps.exports.utils import full_model_to_dict
from tendenci.apps.emails.models import Email
from tendenci.apps.base.utils import escape_csv


try:
    from tendenci.apps.notifications import models as notification
except:
    notification = None


VALID_DATE_FORMAT = "%m/%d/%Y %H:%M:%S"
EVENT_FIELDS = [
    "type",
    "title",
    "description",
    "all_day",
    "start_dt",
    "end_dt",
    "timezone",
    "on_weekend",
    "external_url",
]

PLACE_FIELDS = [
    "place__name",
    "place__description",
    "place__address",
    "place__city",
    "place__state",
    "place__zip",
    "place__country",
    "place__url",
]

def do_events_financial_export(**kwargs):
    identifier = kwargs['identifier']
    user_id = kwargs['user_id']
    try:
        user_id = int(user_id)
    except:
        user_id = None

    start_dt = kwargs['start_dt']
    if start_dt:
        try:
            start_dt = dparser.parse(start_dt)
        except:
            start_dt = None
    end_dt = kwargs['end_dt']
    if end_dt:
        try:
            end_dt = dparser.parse(end_dt)
        except:
            end_dt = None
    sort_by = kwargs['sort_by']
    if sort_by not in ['start_dt', 'groups__name']:
        sort_by = 'start_dt'
    sort_direction = kwargs['sort_direction']
    if sort_direction not in ['', '-']:
        sort_direction = ''

    events = Event.objects.all()

    if start_dt and end_dt:
        events = events.filter(Q(start_dt__gte=start_dt) & Q(start_dt__lte=end_dt))
    events = events.order_by('{0}{1}'.format(sort_direction, sort_by))
    
    show_discount_count = False
    for event in events:
        if event.discount_count > 0:
            show_discount_count = True
            break
    
    currency_symbol = get_setting('site', 'global', 'currencysymbol')
    
    field_list = ['Event ID', 'Event Title', 'Event Date', 'Group Name',
                  '# of Registrants',]
    if show_discount_count:
        field_list.append('# of Discount')
    field_list += ['Registration Total ({})'.format(currency_symbol),
                  'Add-On Total ({})'.format(currency_symbol),
                  'Complete Event Total ({})'.format(currency_symbol),
                  'Amount Collected ({})'.format(currency_symbol),
                  'Amount Due ({})'.format(currency_symbol),]
    file_name_temp = 'export/events/%s_temp.csv' % identifier
    with default_storage.open(file_name_temp, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(field_list)
        
        for event in events:
            groups = ', '.join(event.groups.values_list('name', flat=True))
            row = [event.id, event.title, event.start_dt, groups,
                   event.registrants_count(),]
            if show_discount_count:
                row.append(event.discount_count)
            row += [event.registration_total,
                    event.addons_total, event.money_total,
                    event.money_collected, event.money_outstanding]
            csv_writer.writerow(row)
            
    # rename the file name
    file_name = 'export/events/%s.csv' % identifier
    default_storage.save(file_name, default_storage.open(file_name_temp, 'rb'))
    print('Done. ', file_name)
    
    # notify user that export is ready to download
    [user] = User.objects.filter(pk=user_id)[:1] or [None]
    if user and validate_email(user.email):
        download_url = reverse('event.reports.financial.export_download', args=[identifier])

        site_url = get_setting('site', 'global', 'siteurl')
        site_display_name = get_setting('site', 'global', 'sitedisplayname')
        parms = {
            'download_url': download_url,
            'user': user,
            'site_url': site_url,
            'site_display_name': site_display_name,
            'start_dt': start_dt,
            'end_dt': end_dt,}

        subject = render_to_string(
            template_name='events/notices/financial_export_ready_subject.html', context=parms)
        subject = subject.strip('\n').strip('\r')

        body = render_to_string(
            template_name='events/notices/financial_export_ready_body.html', context=parms)

        email = Email(
            recipient=user.email,
            subject=subject,
            body=body)
        email.send()

    # delete the temp file
    default_storage.delete(file_name_temp)
    
    

def render_event_email(event, email):
    """
    Render event email subject and body.
    """
    context = {}
    context['event_title'] = event.title
    context['event_date'] = format_datetime_range(event.start_dt, event.end_dt)
    context['event_location'] = ''
    if event.place:
        context['event_location'] += '<div><strong>Location</strong>:</div>'
        if event.place.name:
            context['event_location']  += '%s<br />' % event.place.name
        if event.place.address:
            context['event_location']  += '%s<br />' % event.place.address
        if event.place.city or event.place.state or event.place.zip:
            context['event_location']  += '%s %s %s' % (
                                            event.place.city,
                                            event.place.state,
                                            event.place.zip)
    context['event_link'] = '<a href="%s">%s</a>' % (
                            reverse('event', args=[event.id]),
                            event.title
                                                     )
    template = engines['django'].from_string(email.subject)
    email.subject = template.render(context=context)

    email.body = email.body.replace('event_location', 'event_location|safe')
    email.body = email.body.replace('event_link', 'event_link|safe')
    template = engines['django'].from_string(email.body)
    email.body = template.render(context=context)

    return email


def get_default_reminder_template(event):
    from tendenci.apps.events.forms import EMAIL_AVAILABLE_TOKENS

    context = {}
    for token in EMAIL_AVAILABLE_TOKENS:
        context[token] = '{{ %s }}' % token
    return render_to_string(template_name='events/default_email.html',
                           context=context)


def get_ACRF_queryset(event=None):
    """Get the queryset for the available custom registration forms to use for this event
        (include all custom reg forms that are not used by any other events)
    """
    rc_reg_form_ids = []
    rcp_reg_form_ids = []
    if event and event.registration_configuration:
        reg_conf = event.registration_configuration
        regconfpricings = event.registration_configuration.regconfpricing_set.all()
        if reg_conf and reg_conf.reg_form:
            rc_reg_form_ids.append(str(reg_conf.reg_form.id))
        if regconfpricings:
            for conf_pricing in regconfpricings:
                if conf_pricing.reg_form:
                    rcp_reg_form_ids.append(str(conf_pricing.reg_form.id))

    sql = """SELECT id
            FROM events_customregform
            WHERE id not in (SELECT reg_form_id
                        FROM events_registrationconfiguration WHERE reg_form_id>0 %s)
            AND id not in (SELECT reg_form_id From events_regconfpricing WHERE reg_form_id>0 %s)
        """
    if rc_reg_form_ids:
        rc = "AND reg_form_id NOT IN (%s)" % ', '.join(rc_reg_form_ids)
    else:
        rc = ''
    if rcp_reg_form_ids:
        rcp = "AND reg_form_id NOT IN (%s)" % ', '.join(rcp_reg_form_ids)
    else:
        rcp = ''
    sql = sql % (rc, rcp)

    # need to return a queryset not raw queryset
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    ids_list = [row[0] for row in rows]

    if not ids_list:
        # no forms available, create one
        initial = {"status": "active",
                   "name": "Default Custom Registration Form",
                   "notes": "This is a default custom registration form.",
                   "creator_username": "default",
                   "owner_username": "default"}

        form = CustomRegForm.objects.create(**initial)
        fixture_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                 'fixtures/customregfield.json')
        with open(fixture_path) as f:
            data = simplejson.loads(f.read())
            map_to_fields = []
            for regfield in data:
                regfield['fields']['form'] = form
                CustomRegField.objects.create(**regfield['fields'])
                if 'map_to_field' in regfield['fields']:
                    map_to_fields.append(regfield['fields']['map_to_field'])

            for field in map_to_fields:
                if field and hasattr(form, str(field)):
                    setattr(form, field, True)

            form.save()

        ids_list = [form.id]

    queryset = CustomRegForm.objects.filter(id__in=ids_list)

    return queryset

def render_registrant_excel(sheet, rows_list, balance_index, styles, start=0):
    for row, row_data in enumerate(rows_list):
        for col, val in enumerate(row_data):
            # styles the date/time fields
            if isinstance(val, datetime):
                style = styles['datetime_style']
            elif isinstance(val, date):
                style = styles['date_style']
            else:
                style = styles['default_style']
                if isinstance(val, str):
                    val = escape_csv(val)

            # style the invoice balance column
            if col == balance_index:
                balance = val
                if not val:
                    balance = 0
                if isinstance(balance, Decimal) and balance > 0:
                    style = styles['balance_owed_style']

            sheet.write(row+start, col, val, style=style)


def get_ievent(request, d, event_id):
    from tendenci.apps.events.models import Event

    site_url = get_setting('site', 'global', 'siteurl')

    event = Event.objects.get(id=event_id)
    e_str = "BEGIN:VEVENT\r\n"

    # date time
    time_zone = event.timezone
    if not time_zone:
        time_zone = settings.TIME_ZONE

    e_str += "DTSTAMP:{}\r\n".format(adjust_datetime_to_timezone(datetime.now(), time_zone, 'UTC').strftime('%Y%m%dT%H%M%SZ'))

    # organizer
    organizers = event.organizer_set.all()
    if organizers:
        organizer_name_list = [organizer.name for organizer in organizers]
        e_str += "ORGANIZER:%s\r\n" % (', '.join(organizer_name_list))

    if event.start_dt:
        start_dt = adjust_datetime_to_timezone(event.start_dt, time_zone, 'UTC')
        start_dt = start_dt.strftime('%Y%m%dT%H%M%SZ')
        e_str += "DTSTART:%s\r\n" % (start_dt)
    if event.end_dt:
        end_dt = adjust_datetime_to_timezone(event.end_dt, time_zone, 'UTC')
        end_dt = end_dt.strftime('%Y%m%dT%H%M%SZ')
        e_str += "DTEND:%s\r\n" % (end_dt)

    # location
    if event.place:
        e_str += "LOCATION:%s\r\n" % (event.place.name)

    e_str += "TRANSP:OPAQUE\r\n"
    e_str += "SEQUENCE:0\r\n"

    # uid
    e_str += "UID:uid%d@%s\r\n" % (event.pk, d['domain_name'])

    event_url = "%s%s" % (site_url, reverse('event', args=[event.pk]))
    d['event_url'] = event_url

    # text description
    e_str += "DESCRIPTION:%s\r\n" % (build_ical_text(event,d))
    #  html description
    e_str += "X-ALT-DESC;FMTTYPE=text/html:%s\r\n" % (build_ical_html(event,d))

    e_str += "SUMMARY:%s\r\n" % strip_tags(event.title)
    e_str += "PRIORITY:5\r\n"
    e_str += "CLASS:PUBLIC\r\n"
    e_str += "BEGIN:VALARM\r\n"
    e_str += "TRIGGER:-PT30M\r\n"
    e_str += "ACTION:DISPLAY\r\n"
    e_str += "DESCRIPTION:Reminder\r\n"
    e_str += "END:VALARM\r\n"
    e_str += "END:VEVENT\r\n"

    return e_str


def get_vevents(user, d):
    from tendenci.apps.events.models import Event

    site_url = get_setting('site', 'global', 'siteurl')

    e_str = ""
    # load only upcoming events by default
    filters = get_query_filters(user, 'events.view_event')
    events = Event.objects.filter(filters).filter(start_dt__gte=datetime.now())
    events = events.order_by('start_dt')
    
    dtstamp = adjust_datetime_to_timezone(datetime.now(), settings.TIME_ZONE, 'UTC').strftime('%Y%m%dT%H%M%SZ')

    for event in events:
        e_str += "BEGIN:VEVENT\r\n"
        e_str += "DTSTAMP:{}\r\n".format(dtstamp)

        # organizer
        organizers = event.organizer_set.all()
        if organizers:
            organizer_name_list = [organizer.name for organizer in organizers]
            e_str += "ORGANIZER:%s\r\n" % (', '.join(organizer_name_list))

        # date time
        time_zone = event.timezone
        if not time_zone:
            time_zone = settings.TIME_ZONE

        if event.start_dt:
            start_dt = adjust_datetime_to_timezone(event.start_dt, time_zone, 'GMT')
            start_dt = start_dt.strftime('%Y%m%dT%H%M%SZ')
            e_str += "DTSTART:%s\r\n" % (start_dt)
        if event.end_dt:
            end_dt = adjust_datetime_to_timezone(event.end_dt, time_zone, 'GMT')
            end_dt = end_dt.strftime('%Y%m%dT%H%M%SZ')
            e_str += "DTEND:%s\r\n" % (end_dt)

        # location
        if event.place:
            e_str += "LOCATION:%s\r\n" % (event.place.name)

        e_str += "TRANSP:OPAQUE\r\n"
        e_str += "SEQUENCE:0\r\n"

        # uid
        e_str += "UID:uid%d@%s\r\n" % (event.pk, d['domain_name'])

        event_url = "%s%s" % (site_url, reverse('event', args=[event.pk]))
        d['event_url'] = event_url

        # text description
        e_str += "DESCRIPTION:%s\r\n" % (build_ical_text(event,d))
        #  html description
        #e_str += "X-ALT-DESC;FMTTYPE=text/html:%s\n" % (build_ical_html(event,d))

        e_str += "SUMMARY:%s\r\n" % strip_tags(event.title)
        e_str += "PRIORITY:5\r\n"
        e_str += "CLASS:PUBLIC\r\n"
        e_str += "BEGIN:VALARM\r\n"
        e_str += "TRIGGER:-PT30M\r\n"
        e_str += "ACTION:DISPLAY\r\n"
        e_str += "DESCRIPTION:Reminder\r\n"
        e_str += "END:VALARM\r\n"
        e_str += "END:VEVENT\r\n"

    return e_str


def build_ical_text(event, d):
    reg8n_guid = d.get('reg8n_guid')
    reg8n_id = d.get('reg8n_id')
    try:
        reg8n_id = int(reg8n_id)
    except:
        reg8n_id = 0
    if not (reg8n_guid and reg8n_id):
        ical_text = "--- This iCal file does *NOT* confirm registration.\r\n"
    else:
        ical_text = "--- "
    ical_text += "Event details subject to change. ---\r\n"
    ical_text += '%s\r\n\r\n' % d['event_url']

    # title
    ical_text += "Event Title: %s\r\n" % strip_tags(event.title)

    # start_dt
    ical_text += 'Start Date / Time: %s %s\r\n' % (event.start_dt.strftime('%b %d, %Y %H:%M %p'), event.timezone)

    # location
    if event.place:
        ical_text += 'Location: %s\r\n' % (event.place.name)

#    # sponsor
#    sponsors = event.sponsor_set.all()
#    if sponsors:
#        sponsor_name_list = [sponsor.name for sponsor in sponsors]
#        ical_text += 'Sponsor: %s\n' % (', '.join(sponsor_name_list))

    # speaker
    speakers = event.speaker_set.all()
    if speakers.count() > 0:
        speaker_name_list = [speaker.name for speaker in speakers]
        ical_text += 'Speaker: %s\r\n' % (', '.join(speaker_name_list))

    # maps
    show_map_link = False
    if (event.place and event.place.address and event.place.city and event.place.state) \
                or (event.place and event.place.address and event.place.zip):
        show_map_link = True
    if show_map_link:
        ical_text += "Google\r\n"
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

        ical_text += "\r\n\r\nForecast\n"
        ical_text += "http://www.weather.com/weather/monthly/%s\r\n\r\n" % (event.place.zip)

    ical_text += strip_tags((event.description).replace('&nbsp;', " "))
    
    if reg8n_guid and reg8n_id:
        if Registration.objects.filter(guid=reg8n_guid, id=reg8n_id, event_id=event.id).exists():
            registration_email_text = event.registration_configuration.registration_email_text
            if registration_email_text:
                ical_text += '%s\r\n' % (strip_tags((event.registration_configuration.registration_email_text).replace('&nbsp;', " ")))

    if not (reg8n_guid and reg8n_id):
        ical_text += "--- This iCal file does *NOT* confirm registration."
    else:
        ical_text += "--- "
    ical_text += "Event details subject to change. ---\r\n\r\n"
    ical_text += "--- By Tendenci - The Open Source AMS for Associations ---\r\n"

    ical_text  = ical_text.replace(';', '\\;')
    ical_text  = ical_text.replace('\n', '\\n')
    ical_text  = ical_text.replace('\r', '\\r')

    return ical_text


def build_ical_html(event, d):
    # disclaimer: registration
    ical_html = "<div>--- This iCal file does *NOT* confirm registration."
    ical_html += "Event details subject to change. ---</div>"

    # title
    ical_html += "<h1>Event Title: %s</h1>" % (event.title)

    ical_html += '<div>%s</div><br />' % d['event_url']

    # start_dt
    ical_html += '<div>When: %s %s</div>' % (event.start_dt.strftime('%b %d, %Y %H:%M %p'), event.timezone)

#    # sponsor
#    sponsors = event.sponsor_set.all()
#    if sponsors:
#        sponsor_name_list = [sponsor.name for sponsor in sponsors]
#        ical_html += '<div>Sponsor: %s</div>' % (', '.join(sponsor_name_list))

    # speaker
    speakers = event.speaker_set.all()
    if speakers:
        speaker_name_list = [speaker.name for speaker in speakers]
        ical_html += '<div>Speaker: %s</div>' % (', '.join(speaker_name_list))

    ical_html += '<br />'

    # maps
    show_map_link = False
    if (event.place and event.place.address and event.place.city and event.place.state) \
                or (event.place and event.place.address and event.place.zip):
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
    
    reg8n_guid = d.get('reg8n_guid')
    reg8n_id = d.get('reg8n_id')
    try:
        reg8n_id = int(reg8n_id)
    except:
        reg8n_id = 0
    if reg8n_guid and reg8n_id:
        if Registration.objects.filter(guid=reg8n_guid, id=reg8n_id, event_id=event.id).exists():
            registration_email_text = event.registration_configuration.registration_email_text
            if registration_email_text:
                ical_html += '<br />'
                ical_html += '<div>%s</div>' % (event.registration_configuration.registration_email_text)

    ical_html += "<div>--- This iCal file does *NOT* confirm registration."
    ical_html += "Event details subject to change. ---</div>"
    ical_html += "<div>--- Tendenci&reg; Software by <a href=\"https://www.tendenci.com\">tendenci.com</a>"
    ical_html += " - The Open Source AMS for Associations ---</div>"

    ical_html  = ical_html.replace(';', '\\;')
    #ical_html  = degrade_tags(ical_html.replace(';', '\\;'))

    return ical_html


def degrade_tags(str):
    # degrade header tags h1, h2..., h6 to font tags for MS outlook
    # h1 --> font size 6
    str = re.sub(r'<h1[^>]*>(.*?)</h1>', r'<div><strong><font size="6">\1</font></strong></div>', str)

    # h2 --> font size 5
    str = re.sub(r'<h2[^>]*>(.*?)</h2>', r'<div><strong><font size="5">\1</font></strong></div>', str)

    # h3 --> font size 4
    str = re.sub(r'<h3[^>]*>(.*?)</h3>', r'<div><strong><font size="4">\1</font></strong></div>', str)

    # h4 --> font size 3
    str = re.sub(r'<h4[^>]*>(.*?)</h4>', r'<div><strong><font size="3">\1</font></strong></div>', str)

    # h5 --> font size 2
    str = re.sub(r'<h5[^>]*>(.*?)</h5>', r'<div><strong><font size="2">\1</font></strong></div>', str)

    # h6 --> font size 1
    str = re.sub(r'<h6[^>]*>(.*?)</h6>', r'<div><strong><font size="1">\1</font></strong></div>', str)

    return str


def get_next_month(month, year):
    # TODO: cleaner way to get next date
    next_month = (month+1)%13
    next_year = year
    if next_month == 0:
        next_month = 1
        next_year += 1

    return (next_month, next_year)

def get_prev_month(month, year):
    # TODO: cleaner way to get previous date
    prev_month = (month-1)%13
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    return (prev_month, prev_year)


def email_registrants(event, email, **kwargs):
    site_url = get_setting('site', 'global', 'siteurl')
    #reg8ns = Registration.objects.filter(event=event)

    payment_status = kwargs.get('payment_status', 'all')

    if payment_status == 'all':
        registrants = event.registrants()
    elif payment_status == 'paid':
        registrants = event.registrants(with_balance=False)
    elif payment_status == 'not-paid':
        registrants = event.registrants(with_balance=True)
    else:
        raise Exception(
            'Acceptable payment_status field value not found'
        )

    # i had these two lines initially to temporarily hold the original email body
    # please DO NOT remove them. Otherwise, all recipients would have the same names.
    # as the first registrant in the email body. - GJQ  4/13/2011
    tmp_body = email.body

    for registrant in registrants:
        if registrant.custom_reg_form_entry:
            first_name = registrant.custom_reg_form_entry.get_value_of_mapped_field('first_name')
            last_name = registrant.custom_reg_form_entry.get_value_of_mapped_field('last_name')
            email.recipient = registrant.custom_reg_form_entry.get_value_of_mapped_field('email')
        else:
            first_name = registrant.first_name
            last_name = registrant.last_name

            email.recipient = registrant.email

        if email.recipient:
            email.body = email.body.replace('[firstname]', first_name)
            email.body = email.body.replace('[lastname]', last_name)
            invoice = registrant.registration.get_invoice()
            if invoice:
                invoicelink = invoice.get_absolute_url_with_guid()
                invoicelink = '<a href="%s%s">%s%s</a>' % (site_url, invoicelink, site_url, invoicelink)
                email.body = email.body.replace('[invoicelink]', invoicelink)
            else:
                email.body = email.body.replace('[invoicelink]', '')
            email.send()

        email.body = tmp_body  # restore to the original

def email_admins(event, total_amount, self_reg8n, reg8n, registrants):
    site_label = get_setting('site', 'global', 'sitedisplayname')
    site_url = get_setting('site', 'global', 'siteurl')
    admins = get_setting('module', 'events', 'admin_emails').split(',')
    notice_recipients = get_setting('site', 'global', 'allnoticerecipients').split(',')
    email_list = [admin.strip() for admin in admins if admin.strip()]

    # additional check just in case admin emails in event settings
    #are also in all notice recipients set on global site settings
    # to avoid email duplications
    for recipient in notice_recipients:
        clean_recipient = recipient.strip()
        if clean_recipient and (clean_recipient not in email_list):
            email_list.append(clean_recipient)

    notification.send_emails(
        email_list,
        'event_registration_confirmation',
        {
            'SITE_GLOBAL_SITEDISPLAYNAME': site_label,
            'SITE_GLOBAL_SITEURL': site_url,
            'self_reg8n': self_reg8n,
            'reg8n': reg8n,
            'registrants': registrants,
            'event': event,
            'total_amount': total_amount,
            'is_paid': reg8n.invoice.balance == 0,
            'reg8n_number': reg8n.registrant_set.all().count(),
            'for_admin': True,
         },
        True, # save notice in db
    )


def save_registration(*args, **kwargs):
    """
    Adds or Updates the Registration Record.
    Updates Registration, Registrant, and Invoice Table.
    """

    user = kwargs.get('user', None)
    event = kwargs.get('event', None)
    payment_method = kwargs.get('payment_method')
    price = kwargs.get('price', None)

    if not isinstance(user, User):
        user = None

    registrant_set_defaults = {
        'user': user,
        'name': '',
        'first_name': kwargs.get('first_name', ''),
        'last_name': kwargs.get('last_name', ''),
        'email': kwargs.get('email', ''),
        'mail_name': '',
        'address': '',
        'city': '',
        'state': '',
        'zip': '',
        'country': '',
        'phone': kwargs.get('phone', ''),
        'company_name': kwargs.get('company_name', ''),
        'position_title': '',
        'amount': price
    }

    # standardize user_account & user_profile
    # consider authenticated and anonymous
    if user:
        user_profile = user.profile

        registrant_set_defaults.update({
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'mail_name': user_profile.display_name,
            'address': user_profile.address,
            'city': user_profile.city,
            'state': user_profile.state,
            'zip': user_profile.zipcode,
            'country': user_profile.country,
            'phone': user_profile.phone,
            'company_name': user_profile.company,
            'position_title': user_profile.position_title,
        })

    # if no name; use email address
    # if not user_profile.display_name:
    # user_profile.display_name = user_profile.email
    try:
        # find registrant using event + email
        registrant = Registrant.objects.get(
            registration__event=event,
            email=registrant_set_defaults['email'],
            cancel_dt=None,
        )
        reg8n = registrant.registration
        created = False
    except: # create registration; then registrant
        reg8n_attrs = {
            "event": event,
            "payment_method": payment_method,
            "amount_paid": str(price),
        }

        # volatile fields
        if user:
            reg8n_attrs["creator"] = user
            reg8n_attrs["owner"] = user

        # create registration
        reg8n = Registration.objects.create(**reg8n_attrs)

        # create registrant
        registrant = reg8n.registrant_set.create(**registrant_set_defaults)

        created = True

    reg8n.save_invoice()
    return (reg8n, created)

def split_table_price(total_price, quantity):
    """
    Split the price for a team.
    Returns a tuple: (first_individual_price, individual_price).
    """
    avg = Decimal(str(round(total_price/quantity, 2)))
    diff = total_price - avg * quantity

    if diff != 0:
        return (avg+diff, avg)
    return (avg, avg)

def apply_discount(amount, discount_amount):
    """
    Take the amount and discount amount as the input,
    return the new amount and discount amount left.
    """
    if discount_amount > amount:
        return 0, discount_amount - amount
    return amount - discount_amount, 0


def get_registrants_prices(*args):
    # Get the list of final prices for registrants
    (request, event, reg_form, registrant_formset, addon_formset,
    price, event_price) = args

    override_table = False
    override_price_table = Decimal(0)
    if event.is_table and request.user.is_superuser:
        override_table = reg_form.cleaned_data.get('override_table', False)
        override_price_table = reg_form.cleaned_data.get('override_price_table', Decimal(0))
        if override_price_table is None:
            override_price_table = 0

    amount_list = []
    tax_list = []
    if event.is_table:
        if override_table:
            amount = override_price_table
        else:
            amount = event_price
        amount_list.append(amount)
        if price and price.tax_rate:
            tax_list.append(amount * price.tax_rate)
        else:
            tax_list.append(0)

    else:
        override_price_total = Decimal(0)
        for i, form in enumerate(registrant_formset.forms):
            override = False
            override_price = Decimal(0)
            if request.user.is_superuser:
                override = form.cleaned_data.get('override', False)
                override_price = form.cleaned_data.get('override_price', Decimal(0))

            price = form.cleaned_data.get('pricing', 0)

            if override:
                amount = override_price
                override_price_total += amount
            else:
                amount = price.price

            amount_list.append(amount)
            tax_list.append(amount * price.tax_rate)
            

    # apply discount if any
    discount_code = reg_form.cleaned_data.get('discount_code', None)
    discount_amount = Decimal(0)
    discount_list = [Decimal(0) for i in range(len(amount_list))]
    if discount_code:
        [discount] = Discount.objects.filter(discount_code=discount_code,
                        apps__model=RegistrationConfiguration._meta.model_name)[:1] or [None]
        if discount and discount.available_for(1):
            amount_list, discount_amount, discount_list, msg = assign_discount(amount_list, discount)
    return amount_list, discount_amount, discount_list, tax_list


def add_registration(*args, **kwargs):
    """
    Add the registration
    Args are split up below into the appropriate attributes
    """
    # arguments were getting kinda long
    # moved them to an unpacked version
    (request, event, reg_form, registrant_formset, addon_formset,
    price, event_price) = args

    total_amount = 0
    count = 0
    event_price = Decimal(str(event_price))

    #kwargs
    admin_notes = kwargs.get('admin_notes', None)
    custom_reg_form = kwargs.get('custom_reg_form', None)
    gratuity = kwargs.get('gratuity', 0)

    override_table = False
    override_price_table = Decimal(0)
    if event.is_table and request.user.is_superuser:
        override_table = reg_form.cleaned_data.get('override_table', False)
        override_price_table = reg_form.cleaned_data.get('override_price_table', Decimal(0))
        if override_price_table is None:
            override_price_table = 0

    # get the list of amount for registrants.
    amount_list, discount_amount, discount_list, tax_list = get_registrants_prices(*args)

    invoice_discount_amount = discount_amount

    reg8n_attrs = {
        "event": event,
        "payment_method": reg_form.cleaned_data.get('payment_method'),
        "amount_paid": str(total_amount),
        "reg_conf_price": price,
        'is_table': event.is_table,
        'override_table': override_table,
        'override_price_table': override_price_table,
        'gratuity': gratuity,
    }
    if event.is_table:
        reg8n_attrs['quantity'] = price.quantity
    if request.user.is_authenticated:
        reg8n_attrs['creator'] = request.user
        reg8n_attrs['owner'] = request.user

    # create registration
    reg8n = Registration.objects.create(**reg8n_attrs)
    discount_code = reg_form.cleaned_data.get('discount_code', None)
    if discount_code:
        [discount] = Discount.objects.filter(discount_code=discount_code,
                        apps__model=RegistrationConfiguration._meta.model_name)[:1] or [None]

    if event.is_table:
        table_individual_first_price, table_individual_price = amount_list[0], Decimal('0')

#    discount_applied = False
    for i, form in enumerate(registrant_formset.forms):
        override = False
        override_price = Decimal(0)
        free_pass_stat = None
        if not event.is_table:
            # set amount = 0 for valid free pass
            use_free_pass = form.cleaned_data.get('use_free_pass', False)
            if use_free_pass:
                from tendenci.apps.corporate_memberships.utils import get_user_corp_membership
                from tendenci.apps.corporate_memberships.models import FreePassesStat
                # check if free pass is still available
                email = form.cleaned_data.get('email', '')
                memberid = form.cleaned_data.get('memberid', '')
                corp_membership = get_user_corp_membership(
                                                member_number=memberid,
                                                email=email)
                if corp_membership and corp_membership.free_pass_avail:
                    free_pass_stat = FreePassesStat(corp_membership=corp_membership,
                                                    event=event)
                    free_pass_stat.set_creator_owner(request.user)
                    free_pass_stat.save()
                    # update free pass status table
            if free_pass_stat:
                amount = Decimal(0)
            else:
                if request.user.is_superuser:
                    override = form.cleaned_data.get('override', False)
                    override_price = form.cleaned_data.get('override_price', Decimal(0))

                price = form.cleaned_data['pricing']

                # this amount has taken account into admin override and discount code
                amount = amount_list[i]

                if discount_code and discount_amount:
                    discount_amount = discount_list[i]
        else:
            # table individual
            if i == 0:
                amount = table_individual_first_price
            else:
                amount = table_individual_price
#            if reg8n.override_table:
#                override = reg8n.override_table
#                override_price = amount

        # the table registration form does not have the DELETE field
        if event.is_table or form not in registrant_formset.deleted_forms:
            registrant_args = [
                form,
                event,
                reg8n,
                price,
                amount
            ]
            registrant_kwargs = {'custom_reg_form': custom_reg_form,
                                 'is_primary': i==0,
                                 'override': override,
                                 'override_price': override_price,
                                 'use_free_pass': False}
            if not event.is_table:
                registrant_kwargs['discount_amount'] = discount_list[i]
            if free_pass_stat:
                registrant_kwargs['use_free_pass'] = True

            registrant = create_registrant_from_form(*registrant_args, **registrant_kwargs)
            total_amount += registrant.amount

            count += 1

            if free_pass_stat:
                free_pass_stat.registrant = registrant
                if registrant.user:
                    free_pass_stat.user = registrant.user
                free_pass_stat.save()

    # create each regaddon
    for form in addon_formset.forms:
        form.save(reg8n)
    addons_price = addon_formset.get_total_price()
    total_amount += addons_price

    # retrieved the addons text
    reg8n.addons_added = reg8n.addons_included
    reg8n.save()

    # update reg8n with the real amount
    reg8n.amount_paid = total_amount
    created = True

    # create invoice
    invoice = reg8n.save_invoice(admin_notes=admin_notes)
    if discount_code and invoice_discount_amount:
        invoice.discount_code = discount_code
        invoice.discount_amount = invoice_discount_amount
        invoice.save()

    if discount_code and discount:
        for dmount in discount_list:
            if dmount > 0:
                DiscountUse.objects.create(
                        discount=discount,
                        invoice=invoice,
                    )

    return (reg8n, created)


def create_registrant_from_form(*args, **kwargs):
    """
    Create the registrant
    Args are split up below into the appropriate attributes.
    NOTE: When updating this be sure to check with the anonymous registration
    impementation of events in the registration module.
    """
    from tendenci.apps.events.forms import FormForCustomRegForm

    # arguments were getting kinda long
    # moved them to an unpacked version
    form, event, reg8n, \
    price, amount = args

    registrant = Registrant()
    registrant.registration = reg8n
    registrant.pricing = price
    registrant.amount = amount
    registrant.override = kwargs.get('override', False)
    registrant.override_price = kwargs.get('override_price')
    registrant.discount_amount = kwargs.get('discount_amount', Decimal(0))
    if registrant.override_price is None:
        registrant.override_price = Decimal(0)
    registrant.is_primary = kwargs.get('is_primary', False)
    custom_reg_form = kwargs.get('custom_reg_form', None)
    registrant.use_free_pass = kwargs.get('use_free_pass', False)
    registrant.memberid = form.cleaned_data.get('memberid', '')
    registrant.reminder = form.cleaned_data.get('reminder', False)

    if custom_reg_form and isinstance(form, FormForCustomRegForm):
        entry = form.save(event)
        registrant.custom_reg_form_entry = entry
        user = form.get_user()
        if not user.is_anonymous:
            registrant.user = user
            entry.set_group_subscribers(user)
        registrant.initialize_fields()
    else:
        registrant.salutation = form.cleaned_data.get('salutation', '') or ''
        registrant.first_name = form.cleaned_data.get('first_name', '') or ''
        registrant.last_name = form.cleaned_data.get('last_name', '') or ''
        registrant.mail_name = form.cleaned_data.get('mail_name', '') or ''
        registrant.email = form.cleaned_data.get('email', '') or ''
        registrant.position_title = form.cleaned_data.get('position_title', '') or ''
        registrant.company_name = form.cleaned_data.get('company_name', '') or ''
        registrant.phone = form.cleaned_data.get('phone', '') or ''
        registrant.address = form.cleaned_data.get('address', '') or ''
        registrant.city = form.cleaned_data.get('city', '') or ''
        registrant.state = form.cleaned_data.get('state', '') or ''
        registrant.zip = form.cleaned_data.get('zip_code', '') or ''
        registrant.country = form.cleaned_data.get('country', '') or ''
        registrant.meal_option = form.cleaned_data.get('meal_option', '') or ''
        registrant.comments = form.cleaned_data.get('comments', '') or ''

        if registrant.email:
            users = User.objects.filter(email=registrant.email)
            if users:
                registrant.user = users[0]

    registrant.save()
    add_sf_attendance(registrant, event)
    return registrant


def gen_pricing_dict(price, qualifies, failure_type, admin=False):
    """
    Generates a pricing dict based on the current date.
    Disregards time if user.profile.is_superuser is set to True.
    """
    now = datetime.now()
    if admin:
        pricing = {
            'price': price,
            'amount': price.price,
            'qualifies': qualifies,
            'failure_type': failure_type,
            'position': price.position
        }
    else:
        if now >= price.start_dt and now <= price.end_dt:
            pricing = {
                'price': price,
                'amount': price.price,
                'qualifies': qualifies,
                'failure_type': failure_type,
                'position': price.position
            }
        else:
            pricing = {}
    return pricing


def get_pricing(user, event, pricing=None):
    """
    Get a list of qualified pricing in a dictionary
    form with keys as helpers:

    qualified: boolean that tells you if they qualify
               to use this price

    price: instance of the RegConfPricing model

    type: string that holds what price type (early,
          regular or late)

    failure_type: string of what permissions it failed on
    """
    pricing_list = []
    limit = event.get_limit()
    spots_taken = get_event_spots_taken(event)
    spots_left = limit - spots_taken
    if not pricing:
        pricing = RegConfPricing.objects.filter(
            reg_conf=event.registration_configuration,
            status=True,
        )

    # iterate and create a dictionary based
    # on dates and permissions
    # gen_pricing_dict(price_instance, qualifies)
    for price in pricing:
        qualifies = True

        # Admins are always true
        # This should always be at the top of this code
        if user.profile.is_superuser:
            qualifies = True
            pricing_list.append(gen_pricing_dict(
               price,
               qualifies,
               '',
               admin=True)
            )
            continue

        # limits
        if limit > 0:
            if spots_left < price.quantity:
              qualifies = False
              pricing_list.append(gen_pricing_dict(
                price,
                qualifies,
                'limit')
              )
              continue

        # public pricing is always true
        if price.allow_anonymous:
            qualifies = True
            pricing_list.append(gen_pricing_dict(
               price,
               qualifies,
               '')
            )
            continue

        # Admin only price
        if not any([price.allow_user, price.allow_anonymous, price.allow_member, price.groups.all()]):
            if not user.profile.is_superuser:
                continue

        # User permissions
        if price.allow_user and not user.is_authenticated:
            qualifies = False
            pricing_list.append(gen_pricing_dict(
               price,
               qualifies,
               'user')
            )
            continue

        group_member = False
        if price.groups.all():
            for group in price.groups.all():
                if group.is_member(user):
                    group_member = True
                    break

        # Group and Member permissions
        if price.groups.all() and price.allow_member:
            qualifies = False

            if group_member or user.profile.is_member:
                qualifies = True
                pricing_list.append(gen_pricing_dict(
                   price,
                   qualifies,
                   '')
                )
                continue

        # Group permissions
        if price.groups.all() and not group_member:
            qualifies = False
            pricing_list.append(gen_pricing_dict(
               price,
               qualifies,
               'group')
            )
            continue

        # Member permissions
        if price.allow_member and not user.profile.is_member:
            qualifies = False
            pricing_list.append(gen_pricing_dict(
               price,
               qualifies,
               'member')
            )
            continue

        # pricing is true if doesn't get stopped above
        pricing_list.append(gen_pricing_dict(
           price,
           qualifies,
           '')
        )

    # pop out the empty ones if they exist
    pricing_list = [i for i in pricing_list if i]

    # sort the pricing from smallest to largest
    # by price
    sorted_pricing_list = []
    if pricing_list:
        sorted_pricing_list = sorted(
            pricing_list,
            key=lambda k:( k['position'], k['amount'])
        )

        # set a default pricing on the first
        # one that qualifies
        for price in sorted_pricing_list:
            if price['qualifies']:
                price.update({
                    'default': True,
                })
                break

    return sorted_pricing_list


def count_event_spots_taken(event):
    """
    Return current event attendance
    Not counting canceled registrants
    """
    return Registration.objects.filter(
        event=event,
        registrant__cancel_dt__isnull=True
    ).count()


def get_event_spots_taken(event):
    """
    Get registration count for event
    """
    # this method once used index to cache
    # the value and avoid database hits
    # we can review this method once we're
    # using memecache

    # return spots taken, append property [store in memory]
    event.spots_taken = getattr(event, 'spots_taken', count_event_spots_taken(event))
    return event.spots_taken


def registration_earliest_time(event, pricing=None):
    """
    Get the earlist time out of all the pricing.
    This will not consider any registrations that have ended.
    """

    if not pricing:
        pricing = RegConfPricing.objects.filter(
            reg_conf=event.registration_configuration,
            status=True,
        )

    pricing = pricing.filter(end_dt__gt=datetime.now()).order_by('start_dt')

    try:
        return pricing[0].start_dt
    except IndexError:
        return None

def registration_has_started(event, pricing=None):
    """
    Check all times and make sure the registration has
    started
    """
    reg_started = []

    if not pricing:
        pricing = RegConfPricing.objects.filter(
            reg_conf=event.registration_configuration,
            status=True,
        )

    for price in pricing:
        reg_started.append(
            price.registration_has_started
        )

    return any(reg_started)

def registration_has_ended(event, pricing=None):
    """
    Check all times and make sure the registration has
    ended
    """
    reg_ended = []

    if not pricing:
        pricing = RegConfPricing.objects.filter(
            reg_conf=event.registration_configuration,
            status=True,
        )

    for price in pricing:
        reg_ended.append(
            price.registration_has_ended
        )

    return all(reg_ended)

def registration_has_recently_ended(event, pricing=None):
    """
    Check all times and make sure the registration has
    recently ended
    """
    reg_ended = []

    if not pricing:
        pricing = RegConfPricing.objects.filter(
            reg_conf=event.registration_configuration,
            status=True,
        )

    for price in pricing:
        reg_ended.append(
            price.registration_has_recently_ended
        )

    return all(reg_ended)

def clean_price(price, user):
    """
    Used to validate request.POST.price in the multi-register view.
    amount is not validated if user is admin.
    """
    price_pk, amount = price.split('-')
    price = RegConfPricing.objects.get(pk=price_pk, status=True)
    amount = Decimal(str(amount))

    if amount != price.price and not user.profile.is_superuser:
        raise ValueError("Invalid price amount")

    return price, price_pk, amount

def copy_event(event, user, reuse_rel=False):
    #copy event
    new_event = Event.objects.create(
        title = event.title,
        entity = event.entity,
        description = event.description,
        timezone = event.timezone,
        type = event.type,
        image = event.image,
        start_dt = event.start_dt,
        end_dt = event.end_dt,
        all_day = event.all_day,
        on_weekend = event.on_weekend,
        mark_registration_ended = event.mark_registration_ended,
        private_slug = event.private_slug,
        password = event.password,
        tags = event.tags,
        external_url = event.external_url,
        priority = event.priority,
        display_event_registrants = event.display_event_registrants,
        display_registrants_to = event.display_registrants_to,
        allow_anonymous_view = False,
        allow_user_view = event.allow_user_view,
        allow_member_view = event.allow_member_view,
        allow_user_edit = event.allow_user_edit,
        allow_member_edit = event.allow_member_edit,
        creator = user,
        creator_username = user.username,
        owner = user,
        owner_username = user.username,
        status = event.status,
        status_detail = event.status_detail,
    )
    new_event.groups.add(*list(event.groups.all()))

    #copy place
    place = event.place
    if place:
        if reuse_rel:
            new_event.place = place
        else:
            new_place = Place.objects.create(
                name = place.name,
                description = place.description,
                address = place.address,
                city = place.city,
                state = place.state,
                zip = place.zip,
                country = place.country,
                url = place.url,
            )
            new_event.place = new_place
        new_event.save()

    #copy speakers
    for speaker in event.speaker_set.all():
        if reuse_rel:
            speaker.event.add(new_event)
        else:
            new_speaker = Speaker.objects.create(
                user = speaker.user,
                name = speaker.name,
                description = speaker.description,
            )
            new_speaker.event.add(new_event)

    #copy organizers
    for organizer in event.organizer_set.all():
        if reuse_rel:
            organizer.event.add(new_event)
        else:
            new_organizer = Organizer.objects.create(
                user = organizer.user,
                name = organizer.name,
                description = organizer.description,
            )
            new_organizer.event.add(new_event)

    #copy sponsor
    for sponsor in event.sponsor_set.all():
        if reuse_rel:
            sponsor.event.add(new_event)
        else:
            new_sponsor = Sponsor.objects.create(
                description = sponsor.description,
            )
            new_sponsor.event.add(new_event)

    #copy registration configuration
    old_regconf = event.registration_configuration
    if old_regconf:
        new_regconf = RegistrationConfiguration.objects.create(
            payment_required = old_regconf.payment_required,
            limit = old_regconf.limit,
            enabled = old_regconf.enabled,
            require_guests_info = old_regconf.require_guests_info,
            is_guest_price = old_regconf.is_guest_price,
            discount_eligible = old_regconf.discount_eligible,
            display_registration_stats = old_regconf.display_registration_stats,
            use_custom_reg_form = old_regconf.use_custom_reg_form,
            reg_form = old_regconf.reg_form,
            bind_reg_form_to_conf_only = old_regconf.bind_reg_form_to_conf_only,
            send_reminder = old_regconf.send_reminder,
            reminder_days = old_regconf.reminder_days,
            registration_email_text = old_regconf.registration_email_text,
        )
        new_regconf.payment_method.set(old_regconf.payment_method.all())
        new_regconf.save()
        new_event.registration_configuration = new_regconf
        new_event.save()

        #copy regconf pricings
        for pricing in old_regconf.regconfpricing_set.filter(status=True):
            new_pricing = RegConfPricing.objects.create(
                reg_conf = new_regconf,
                title = pricing.title,
                quantity = pricing.quantity,
                price = pricing.price,
                reg_form = pricing.reg_form,
                start_dt = pricing.start_dt,
                end_dt = pricing.end_dt,
                allow_anonymous = pricing.allow_anonymous,
                allow_user = pricing.allow_user,
                allow_member = pricing.allow_member,
            )
            new_pricing.groups.set(pricing.groups.all())

    #copy addons
    for addon in event.addon_set.all():
        new_addon = Addon.objects.create(
            event = new_event,
            title = addon.title,
            price = addon.price,
            group = addon.group,
            default_yes = addon.default_yes,
            allow_anonymous = addon.allow_anonymous,
            allow_user = addon.allow_user,
            allow_member = addon.allow_member,
            status = addon.status,
        )
        # copy addon options
        for option in addon.options.all():
            AddonOption.objects.create(
                addon = new_addon,
                title = option.title,
            )

    return new_event

def get_active_days(event):
    """
    Returns date ranges where the event is active.
    Each date range is a 2-tuple of dates.
    [(start_dt, end_dt), (start_dt, end_dt)]
    """
    current_dt = event.start_dt
    end_dt = event.end_dt
    day_list = []

    start_dt = current_dt
    while(current_dt<end_dt):
        current_dt += timedelta(days=1)
        start_weekday = start_dt.strftime('%a')
        current_weekday = current_dt.strftime('%a')
        if start_weekday == 'Sun' or start_weekday == 'Sat':
            #skip if the event starts on a weekday
            start_dt = current_dt
        else:
            if (current_weekday == 'Sun' or current_weekday == 'Sat') and not event.on_weekend:
                day_list.append((start_dt, current_dt-timedelta(days=1)))
                start_dt = current_dt
    next_dt = current_dt-timedelta(days=1)
    next_weekday = next_dt.strftime('%a')
    if next_weekday != 'Sun' and next_weekday != 'Sat':
        day_list.append((start_dt, next_dt))

    return day_list

def get_custom_registrants_initials(entries, **kwargs):
    initials = []
    for entry in entries:
        fields_d = {}
        field_entries = entry.field_entries.all()
        for field_entry in field_entries:
            if field_entry.field.map_to_field:
                field_key = field_entry.field.map_to_field
            else:
                field_key = 'field_%d' % field_entry.field.id
            fields_d[field_key] = field_entry.value
        initials.append(fields_d)
    return initials


def get_recurrence_dates(repeat_type, start_dt, end_dt, frequency, recur_every):
    weeknum = math.floor((start_dt.day - 1)/7) + 1
    if weeknum > 4:
        weeknum = -1
    weekday = datetime.weekday(start_dt)
    if repeat_type == RecurringEvent.RECUR_DAILY:
        return rrule(DAILY, dtstart=start_dt, until=end_dt, interval=frequency)
    elif repeat_type == RecurringEvent.RECUR_WEEKLY:
        return rrule(WEEKLY, dtstart=start_dt, until=end_dt, interval=frequency)
    elif repeat_type == RecurringEvent.RECUR_MONTHLY:
        if recur_every == 'date':
            return rrule(MONTHLY, dtstart=start_dt, until=end_dt, interval=frequency)
        else:
            return rrule(MONTHLY, dtstart=start_dt, until=end_dt, interval=frequency, bysetpos=weeknum, byweekday=weekday)
    elif repeat_type == RecurringEvent.RECUR_YEARLY:
        if recur_every == 'date':
            return rrule(YEARLY, dtstart=start_dt, until=end_dt, interval=frequency)
        else:
            return rrule(YEARLY, dtstart=start_dt, until=end_dt, interval=frequency, bymonth=start_dt.month, bysetpos=weeknum, byweekday=weekday)


def event_import_process(import_i, preview=True):
    """
    This function processes each row and store the data
    in the event_object_dict. Then it updates the database
    if preview=False.
    """
    #print("START IMPORT PROCESS")
    data_dict_list = extract_from_excel(str(import_i.file))

    event_obj_list = []
    invalid_list = []

    import_i.total_invalid = 0
    import_i.total_created = 0
    if not preview:  # update import status
        import_i.status = "processing"
        import_i.save()

    try:
        # loop through the file's entries and determine valid imports
        start = 0
        finish = len(data_dict_list)
        for r in range(start, finish):
            invalid = False
            event_object_dict = {}
            data_dict = data_dict_list[r]

            for key in data_dict:
                if isinstance(data_dict[key], str):
                    event_object_dict[key] = data_dict[key].strip()
                else:
                    event_object_dict[key] = data_dict[key]

            event_object_dict['ROW_NUM'] = data_dict['ROW_NUM']

            # Validate date fields
            try:
                datetime.strptime(event_object_dict["start_dt"], VALID_DATE_FORMAT)
                datetime.strptime(event_object_dict["end_dt"], VALID_DATE_FORMAT)
            except ValueError as e:
                invalid = True
                invalid_reason = "INVALID DATE FORMAT. SHOULD BE: %s" % VALID_DATE_FORMAT

            try:
                timezone(event_object_dict["timezone"])
            except UnknownTimeZoneError as e:
                invalid = True
                invalid_reason = "UNKNOWN TIMEZONE %s" % event_object_dict["timezone"]

            if invalid:
                event_object_dict['ERROR'] = invalid_reason
                event_object_dict['IS_VALID'] = False
                import_i.total_invalid += 1
                if not preview:
                    invalid_list.append({
                        'ROW_NUM': event_object_dict['ROW_NUM'],
                        'ERROR': event_object_dict['ERROR']})
            else:
                event_object_dict['IS_VALID'] = True
                import_i.total_created += 1

                if not preview:
                    event_import_dict = {}
                    event_import_dict['ACTION'] = 'insert'
                    event = do_event_import(event_object_dict)
                    event_import_dict = {}
                    event_import_dict['event'] = event
                    event_import_dict['ROW_NUM'] = event_object_dict['ROW_NUM']
                    event_obj_list.append(event_import_dict)

            if preview:
                event_obj_list.append(event_object_dict)

        if not preview:  # save import status
            import_i.status = "completed"
            import_i.save()
    except Exception as e:
        import_i.status = "failed"
        import_i.failure_reason = str(e)
        import_i.save()

    #print("END IMPORT PROCESS")
    return event_obj_list, invalid_list


def do_event_import(event_object_dict):
    """Creates and Event and Place for the given event_object_dict
    """
    event = Event()
    place = Place()

    # assure the correct fields get the right value types
    color_set = TypeColorSet.objects.all()[0]  # default color set
    for field in EVENT_FIELDS:
        if field in event_object_dict:
            if field == "type":
                try:
                    event_type = Type.objects.get(name=event_object_dict[field])
                except Type.DoesNotExist:
                    event_type = Type(
                                    name=event_object_dict[field],
                                    slug=slugify(event_object_dict[field]),
                                    color_set=color_set
                                    )
            else:
                field_type = Event._meta.get_field(field)
                if isinstance(field_type, models.DateTimeField):
                    setattr(event, field, datetime.strptime(event_object_dict[field], VALID_DATE_FORMAT))
                elif isinstance(field_type, models.NullBooleanField):
                    if event_object_dict[field].lower() == "false" or event_object_dict[field] == "0":
                        setattr(event, field, False)
                    else:
                        setattr(event, field, True)
                else:  # assume its a string
                    if field_type.max_length:
                        setattr(event, field, str(event_object_dict[field])[:field_type.max_length])
                    else:
                        setattr(event, field, str(event_object_dict[field]))

    for field in PLACE_FIELDS:
        if field in event_object_dict:
            p_field = field.replace('place__', '')
            field_type = Place._meta.get_field(p_field)
            if isinstance(field_type, models.DateTimeField):
                setattr(place, p_field, datetime.strptime(event_object_dict[field], VALID_DATE_FORMAT))
            elif isinstance(field_type, models.NullBooleanField):
                setattr(place, p_field, bool(ast.literal_eval(event_object_dict[field])))
            else:  # assume its a string
                if field_type.max_length:
                    setattr(place, p_field, str(event_object_dict[field])[:field_type.max_length])
                else:
                    setattr(place, p_field, str(event_object_dict[field]))

    event_type.save()
    place.save()

    event.type = event_type
    event.place = place
    event.save()

    return event


def add_sf_attendance(registrant, event):
    from tendenci.apps.profiles.models import Profile

    if hasattr(settings, 'SALESFORCE_AUTO_UPDATE') and settings.SALESFORCE_AUTO_UPDATE:
        sf = get_salesforce_access()
        if sf:
            # Make sure we have a complete user detail from registrants
            # which do not have an associated user. This is because the
            # contact ID will not be stored.

            # strip spaces to avoid duplicates being created
            registrant.first_name = registrant.first_name.strip(' ')
            registrant.last_name = registrant.last_name.strip(' ')
            registrant.email = registrant.email.strip(' ')

            contact_requirements = (registrant.first_name,
                                    registrant.last_name,
                                    registrant.email)
            contact_id = None
            # Get Salesforce Contact ID
            if registrant.user:
                try:
                    profile = registrant.user.profile
                except Profile.DoesNotExist:
                    profile = Profile.objects.create_profile(user=registrant.user)

                # first, last, and email required
                profile.user.first_name = profile.user.first_name or registrant.first_name
                profile.user.last_name = profile.user.last_name or registrant.last_name
                profile.user.email = profile.user.email or registrant.email
                profile.user.save()

                # update profile details
                profile.position_title = profile.position_title or registrant.position_title
                profile.phone = profile.phone or registrant.phone
                profile.address = profile.address or registrant.address
                profile.city = profile.city or registrant.city
                profile.state = profile.state or registrant.state
                profile.country = profile.country or registrant.country
                profile.zipcode = profile.zipcode or registrant.zip
                profile.company = profile.company or registrant.company_name
                profile.position_title = profile.position_title or registrant.position_title

                profile.save()

                contact_id = create_salesforce_contact(profile)

            elif all(contact_requirements):
                # Query for a duplicate entry in salesforce
                # saleforce blocks the request if email is already in their system - so just checking email
                result = sf.query("SELECT Id FROM Contact WHERE Email='%s'" % registrant.email.replace("'", "''"))
                if result['records']:
                    contact_id = result['records'][0]['Id']
                else:
                    contact = sf.Contact.create({
                        'FirstName':registrant.first_name,
                        'LastName':registrant.last_name,
                        'Title':registrant.position_title,
                        'Email':registrant.email,
                        'Phone':registrant.phone,
                        'MailingStreet':registrant.address,
                        'MailingCity':registrant.city,
                        'MailingState':registrant.state,
                        'MailingCountry':registrant.country,
                        'MailingPostalCode':registrant.zip
                        })
                    # update field Company_Name__c
                    if registrant.company_name and 'Company_Name__c' in contact:
                        sf.Contact.update(contact['id'], {'Company_Name__c': registrant.company_name})

                    contact_id = contact['id']

            if contact_id:
                result = sf.Event.create({
                    'WhoId':contact_id,
                    'Subject':event.title,
                    'StartDateTime':event.start_dt.isoformat(),
                    'EndDateTime':event.end_dt.isoformat()})


def create_member_registration(user, event, form):

    from tendenci.apps.profiles.models import Profile

    pricing = form.cleaned_data['pricing']
    reg_attrs = {'event': event,
                 'reg_conf_price': pricing,
                 'amount_paid': pricing.price,
                 'creator': user,
                 'owner': user}

    for mem_id in form.cleaned_data['member_ids'].split(','):
        mem_id = mem_id.strip()
        [member] = Profile.objects.filter(member_number=mem_id,
                                          status_detail='active')[:1] or [None]
        if member:
            exists = event.registrants().filter(user=member.user)
            if not exists:
                registration = Registration.objects.create(**reg_attrs)
                registrant_attrs = {'registration': registration,
                                    'user': member.user,
                                    'first_name': member.user.first_name,
                                    'last_name': member.user.last_name,
                                    'email': member.user.email,
                                    'is_primary': True,
                                    'amount': pricing.price,
                                    'pricing': pricing}
                Registrant.objects.create(**registrant_attrs)
                registration.save_invoice()


def get_week_days(tgtdate, cal):
    weekdays = list(cal.iterweekdays())
    tgt_weekday = tgtdate.weekday()
    tgt_index = weekdays.index(tgt_weekday)
    b_ctr = tgt_index - 0
    f_ctr = 6 - tgt_index
    days = []
    for ctr in range(-b_ctr, f_ctr+1):
        days.append(tgtdate + timedelta(days=ctr))
    return days


def process_event_export(start_dt=None, end_dt=None, event_type=None,
                         identifier=u'', user_id=0):
    """
    This exports all events data and registration configuration.
    This export needs to be able to handle additional columns for each
    instance of Pricing, Speaker, and Addon.
    This export does not include registrant data.
    """
    event_fields = [
        'entity',
        'group',
        'type',
        'title',
        'description',
        'all_day',
        'start_dt',
        'end_dt',
        'timezone',
        'private_slug',
        'password',
        'on_weekend',
        'external_url',
        'image',
        'tags',
        'allow_anonymous_view',
        'allow_user_view',
        'allow_member_view',
        'allow_user_edit',
        'allow_member_edit',
        'create_dt',
        'update_dt',
        'creator',
        'creator_username',
        'owner',
        'owner_username',
        'status',
        'status_detail',
    ]
    place_fields = [
        'name',
        'description',
        'address',
        'city',
        'state',
        'zip',
        'country',
        'url',
    ]
    configuration_fields = [
        'payment_method',
        'payment_required',
        'limit',
        'enabled',
        'is_guest_price',
        'use_custom_reg_form',
        'reg_form',
        'bind_reg_form_to_conf_only',
    ]
    speaker_fields = [
        'name',
        'description',
    ]
    organizer_fields = [
        'name',
        'description',
    ]
    pricing_fields = [
        'title',
        'quantity',
        'groups',
        'price',
        'reg_form',
        'start_dt',
        'end_dt',
        'allow_anonymous',
        'allow_user',
        'allow_member',
        'status',
    ]

    events = Event.objects.filter(status=True)
    if start_dt and end_dt:
        events = events.filter(start_dt__gte=start_dt, start_dt__lte=end_dt)
    if event_type:
        events = events.filter(type=event_type)

    max_speakers = events.annotate(num_speakers=Count('speaker')).aggregate(Max('num_speakers'))['num_speakers__max']
    max_organizers = events.annotate(num_organizers=Count('organizer')).aggregate(Max('num_organizers'))['num_organizers__max']
    max_pricings = events.annotate(num_pricings=Count('registration_configuration__regconfpricing')).aggregate(Max('num_pricings'))['num_pricings__max']

    data_row_list = []

    for event in events:
        data_row = []
        # event setup
        event_d = full_model_to_dict(event, fields=event_fields)
        for field in event_fields:
            value = None
            if field == 'entity':
                if event.entity:
                    value = event.entity.entity_name
            elif field == 'type':
                if event.type:
                    value = event.type.name
            elif field == 'group':
                groups = event.groups.values_list('name', flat=True)
                if groups:
                    value = ', '.join(groups)
            elif field in event_d:
                value = event_d[field]
            value = str(value).replace(os.linesep, ' ').rstrip()
            value = escape_csv(value)
            data_row.append(value)

        if event.place:
            # place setup
            place_d = full_model_to_dict(event.place)
            for field in place_fields:
                value = place_d[field]
                value = str(value).replace(os.linesep, ' ').rstrip()
                value = escape_csv(value)
                data_row.append(value)

        if event.registration_configuration:
            # config setup
            conf_d = full_model_to_dict(event.registration_configuration)
            for field in configuration_fields:
                if field == "payment_method":
                    value = event.registration_configuration.payment_method.all()
                    value = value.values_list('human_name', flat=True)
                else:
                    value = conf_d[field]
                value = str(value).replace(os.linesep, ' ').rstrip()
                value = escape_csv(value)
                data_row.append(value)

        if event.speaker_set.all():
            # speaker setup
            for speaker in event.speaker_set.all():
                speaker_d = full_model_to_dict(speaker)
                for field in speaker_fields:
                    value = speaker_d[field]
                    value = str(value).replace(os.linesep, ' ').rstrip()
                    value = escape_csv(value)
                    data_row.append(value)

        # fill out the rest of the speaker columns
        if event.speaker_set.all().count() < max_speakers:
            for i in range(0, max_speakers - event.speaker_set.all().count()):
                for field in speaker_fields:
                    data_row.append('')

        if event.organizer_set.all():
            # organizer setup
            for organizer in event.organizer_set.all():
                organizer_d = full_model_to_dict(organizer)
                for field in organizer_fields:
                    value = organizer_d[field]
                    value = str(value).replace(os.linesep, ' ').rstrip()
                    value = escape_csv(value)
                    data_row.append(value)

        # fill out the rest of the organizer columns
        if event.organizer_set.all().count() < max_organizers:
            for i in range(0, max_organizers - event.organizer_set.all().count()):
                for field in organizer_fields:
                    data_row.append('')

        reg_conf = event.registration_configuration
        if reg_conf and reg_conf.regconfpricing_set.all():
            # pricing setup
            for pricing in reg_conf.regconfpricing_set.all():
                pricing_d = full_model_to_dict(pricing)
                for field in pricing_fields:
                    if field == 'groups':
                        value = pricing.groups.values_list('name', flat=True)
                    else:
                        value = pricing_d[field]
                    value = str(value).replace(os.linesep, ' ').rstrip()
                    value = escape_csv(value)
                    data_row.append(value)

        # fill out the rest of the pricing columns
        if reg_conf and reg_conf.regconfpricing_set.all().count() < max_pricings:
            for i in range(0, max_pricings - reg_conf.regconfpricing_set.all().count()):
                for field in pricing_fields:
                    data_row.append('')

        data_row_list.append(data_row)

    fields = event_fields + ["place %s" % f for f in place_fields]
    fields = fields + ["config %s" % f for f in configuration_fields]
    for i in range(0, max_speakers):
        fields = fields + ["speaker %s %s" % (i, f) for f in speaker_fields]
    for i in range(0, max_organizers):
        fields = fields + ["organizer %s %s" % (i, f) for f in organizer_fields]
    for i in range(0, max_pricings):
        fields = fields + ["pricing %s %s" % (i, f) for f in pricing_fields]

    identifier = identifier or int(ttime.time())
    file_name_temp = 'export/events/%s_temp.csv' % identifier

    with default_storage.open(file_name_temp, 'wb') as csvfile:
        csv_writer = UnicodeWriter(csvfile, encoding='utf-8')
        csv_writer.writerow(fields)

        for row in data_row_list:
            csv_writer.writerow(row)

    # rename the file name
    file_name = 'export/events/%s.csv' % identifier
    default_storage.save(file_name, default_storage.open(file_name_temp, 'rb'))

    # delete the temp file
    default_storage.delete(file_name_temp)

    # notify user that export is ready to download
    [user] = User.objects.filter(pk=user_id)[:1] or [None]
    if user and user.email:
        download_url = reverse('event.export_download', args=[identifier])

        site_url = get_setting('site', 'global', 'siteurl')
        site_display_name = get_setting('site', 'global', 'sitedisplayname')
        parms = {
            'download_url': download_url,
            'user': user,
            'site_url': site_url,
            'site_display_name': site_display_name,
            'start_dt': start_dt,
            'end_dt': end_dt,
            'type': event_type}

        subject = render_to_string(
            template_name='events/notices/export_ready_subject.html', context=parms)
        subject = subject.strip('\n').strip('\r')

        body = render_to_string(
            template_name='events/notices/export_ready_body.html', context=parms)

        email = Email(
            recipient=user.email,
            subject=subject,
            body=body)
        email.send()
