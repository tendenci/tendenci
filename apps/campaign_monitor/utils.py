from createsend import Client
from django.conf import settings
from site_settings.utils import get_setting
from campaign_monitor.models import Campaign, Template
from createsend import CreateSend, Client
import urllib2
import random
import string

api_key = getattr(settings, 'CAMPAIGNMONITOR_API_KEY', None)
api_password = getattr(settings, 'CAMPAIGNMONITOR_API_PASSWORD', None)
client_id = getattr(settings, 'CAMPAIGNMONITOR_API_CLIENT_ID', None)
CreateSend.api_key = api_key

def random_string(n=32):
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(n))
    
def temporary_id():
    exists = True
    while(exists):
        id = random_string()
        if not Template.objects.filter(template_id=id).exists():
            exists = False
    return id

def sync_campaigns():
    cl = Client(client_id)
    
    print 'Syncing sent campaigns...'
    sent = cl.campaigns()
    for c in sent:
        try:
            campaign = Campaign.objects.get(campaign_id = c.CampaignID)
            print "Updating campaign (%s - %s)" % (c.CampaignID, c.Name)
        except Campaign.DoesNotExist:
            print "Creating campaign (%s - %s)" % (c.CampaignID, c.Name)
            campaign = Campaign(campaign_id = c.CampaignID)
        campaign.subject = c.Subject
        campaign.name = c.Name
        campaign.sent_date = c.SentDate
        campaign.status = 'S'
        campaign.save()
    
    print 'Syncing scheduled campaigns...'
    if hasattr(cl,'scheduled'): scheduled = cl.scheduled()
    else: scheduled = []
    for c in scheduled:
        try:
            campaign = Campaign.objects.get(campaign_id = c.CampaignID)
            print "Updating campaign (%s - %s)" % (c.CampaignID, c.Name)
        except Campaign.DoesNotExist:
            print "Creating campaign (%s - %s)" % (c.CampaignID, c.Name)
            campaign = Campaign(campaign_id = c.CampaignID)
        campaign.subject = c.Subject
        campaign.name = c.Name
        campaign.status = 'C'
        campaign.save()
    
    print 'Syncing draft campaigns...'
    if hasattr(cl,'drafts'): drafts = cl.drafts()
    else: drafts = []
    for c in drafts:
        try:
            campaign = Campaign.objects.get(campaign_id = c.CampaignID)
            print "Updating campaign (%s - %s)" % (c.CampaignID, c.Name)
        except Campaign.DoesNotExist:
            print "Creating campaign (%s - %s)" % (c.CampaignID, c.Name)
            campaign = Campaign(campaign_id = c.CampaignID)
        campaign.subject = c.Subject
        campaign.name = c.Name
        campaign.save()

    print 'Syncing templates...'
    if hasattr(cl,'templates'): templates = cl.templates()
    else: templates = []
    for t in templates:
        try:
            template = Template.objects.get(template_id = t.TemplateID)
            print "Updating campaign (%s - %s)" % (c.CampaignID, c.Name)
        except Template.DoesNotExist:
            print "Creating template (%s - %s)" % (t.TemplateID, t.Name)
            template = Template(template_id = t.TemplateID)
        template.name = t.Name
        template.cm_preview_url = t.PreviewURL
        template.cm_screenshot_url = t.ScreenshotURL
        template.save()
