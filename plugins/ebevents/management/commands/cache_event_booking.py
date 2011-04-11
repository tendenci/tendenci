import os
import urllib2
from BeautifulSoup import BeautifulStoneSoup

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


EVENTBOOKING_XML_URL = 'http://go.eventbooking.com/xml_public.asp?pwl=30CA.5B2115DE'
CACHE_PATH = os.path.join(settings.MEDIA_ROOT,'ebevents')

class Command(BaseCommand):
    """
    Server Load script to cache event booking XML when site is under stress
    IE: NCAA FINAL FOUR
    """
    def handle(self, *args, **options):
        url_object = urllib2.urlopen(EVENTBOOKING_XML_URL, timeout=120)
        xml = url_object.read()

        # write the main list xml file
        with open(os.path.join(CACHE_PATH, 'events_list.xml'), 'w') as f:
            f.write(xml)
        
        # loop through all events and save down individual events xml files
        soup = BeautifulStoneSoup(xml)
        nodes = soup.findAll('event')
        for event in nodes:
            event_id = event.unique_event_id.string
            individual_event_url = '%s&mode=detail&event_id=%s' % (
                EVENTBOOKING_XML_URL,
                event_id
            )

            url_object = urllib2.urlopen(individual_event_url, timeout=120)
            xml = url_object.read()

            # write the main list xml file
            with open(os.path.join(CACHE_PATH, 'event_%s.xml' % event_id), 'w'+) as f:
                f.write(xml)
