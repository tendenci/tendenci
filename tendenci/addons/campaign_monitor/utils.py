import os
import re
import random
import string
import zipfile
import shutil
import datetime
from datetime import timedelta

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from createsend import CreateSend, Client, Subscriber
from createsend.createsend import BadRequest
from createsend import Template as CST

from tendenci.addons.campaign_monitor.models import Campaign, Template
from tendenci.core.site_settings.utils import get_setting

api_key = getattr(settings, 'CAMPAIGNMONITOR_API_KEY', None)
api_password = getattr(settings, 'CAMPAIGNMONITOR_API_PASSWORD', None)
client_id = getattr(settings, 'CAMPAIGNMONITOR_API_CLIENT_ID', None)
auth = {'api_key': api_key}
cl = Client(auth, client_id)

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
    sent = cl.campaigns()
    for c in sent:
        try:
            campaign = Campaign.objects.get(campaign_id = c.CampaignID)
        except Campaign.DoesNotExist:
            campaign = Campaign(campaign_id = c.CampaignID)
        campaign.subject = c.Subject
        campaign.name = c.Name
        campaign.sent_date = c.SentDate
        campaign.web_version_url = c.WebVersionURL
        campaign.total_recipients = c.TotalRecipients
        campaign.status = 'S' #sent
        campaign.save()

    if hasattr(cl,'scheduled'): scheduled = cl.scheduled()
    else: scheduled = []
    for c in scheduled:
        try:
            campaign = Campaign.objects.get(campaign_id = c.CampaignID)
        except Campaign.DoesNotExist:
            campaign = Campaign(campaign_id = c.CampaignID)
        campaign.subject = c.Subject
        campaign.name = c.Name
        campaign.scheduled_date = c.DateScheduled
        campaign.scheduled_time_zone = c.ScheduledTimeZone
        campaign.preview_url = c.PreviewURL
        campaign.status = 'C' #Scheduled
        campaign.save()

    if hasattr(cl,'drafts'): drafts = cl.drafts()
    else: drafts = []
    for c in drafts:
        try:
            campaign = Campaign.objects.get(campaign_id = c.CampaignID)
        except Campaign.DoesNotExist:
            campaign = Campaign(campaign_id = c.CampaignID)
        campaign.subject = c.Subject
        campaign.name = c.Name
        campaign.preview_url = c.PreviewURL
        campaign.save()

def sync_templates(request=None):
    """
    Pushes most recent template updates
    up to Campaign Monitor
    """
    templates = []
    if hasattr(cl,'templates'):
        templates = cl.templates()

    for t in templates:

        try:
            template = Template.objects.get(template_id = t.TemplateID)
        except Template.DoesNotExist:
            template = Template(template_id = t.TemplateID)
            template.name = t.Name
            template.cm_preview_url = t.PreviewURL
            template.cm_screenshot_url = t.ScreenshotURL
        except Exception as e:
            print 'sync template exception', e

        #set up urls
        site_url = get_setting('site', 'global', 'siteurl')
        html_url = unicode("%s%s"%(site_url, template.get_html_url()))
        html_url += "?jump_links=1&articles=1&articles_days=60&news=1&news_days=60&jobs=1&jobs_days=60&pages=1&pages_days=7"
        html_url += "&events=1"
        html_url += "&events_type="
        html_url += "&event_start_dt=%s" % datetime.date.today()
        end_dt = datetime.date.today() + timedelta(days=90)
        html_url += "&event_end_dt=%s" % end_dt

        if template.zip_file:
            if hasattr(settings, 'USE_S3_STORAGE') and settings.USE_S3_STORAGE:
                zip_url = unicode(template.get_zip_url())
            else:
                zip_url = unicode("%s%s"%(site_url, template.get_zip_url()))
        else:
            zip_url = unicode()

        #sync with campaign monitor
        try:
            cst = CST(auth, template_id=template.template_id)
            cst.update(unicode(template.name), html_url, zip_url)
            success = True
        except BadRequest, e:
            success = False
            if request:
                msg_string = 'Bad Request %s: %s' % (e.data.Code, e.data.Message)
                messages.add_message(request, messages.ERROR, _(msg_string))
            else:
                print e.data.Code, e.data.Message
                return
        except Exception, e:
            success = False
            if request:
                msg_string = 'Error: %s' % e
                messages.add_message(request, messages.ERROR, _(msg_string))
            else:
                print e.data.Code, e.data.Message
                return

        #get campaign monitor details
        template.name = t.Name
        template.cm_preview_url = t.PreviewURL
        template.cm_screenshot_url = t.ScreenshotURL
        template.save()
        return success


def extract_files(template):
    if template.zip_file:
        zip_file = zipfile.ZipFile(template.zip_file.file)
        if hasattr(settings, 'USE_S3_STORAGE') and settings.USE_S3_STORAGE:
            # create a tmp directory to extract the zip file
            tmp_dir = 'tmp_%d' % template.id
            path = './%s/campaign_monitor/%s' % (tmp_dir, template.template_id)
            zip_file.extractall(path)
            # upload extracted files to s3
            for root, dirs, files in os.walk(path):
                for name in files:
                    file_path = os.path.join(root, name)
                    dst_file_path = file_path.replace('./%s/' % tmp_dir, '')
                    default_storage.save(dst_file_path,
                                ContentFile(open(file_path).read()))

            # remove the tmp directory
            shutil.rmtree(tmp_dir)
        else:
            path = os.path.join(settings.MEDIA_ROOT,
                                'campaign_monitor',
                                template.template_id)
            zip_file.extractall(path)


def apply_template_media(template):
    """
    Prepends files in content to the media path
    of a given template's zip file contents
    """
    content = unicode(template.html_file.file.read(), "utf-8")
    pattern = r'"[^"]*?\.(?:(?i)jpg|(?i)jpeg|(?i)png|(?i)gif|(?i)bmp|(?i)tif|(?i)css)"'
    repl = lambda x: '"%s/%s"' % (template.get_media_url(), x.group(0).replace('"', ''))
    new_content = re.sub(pattern, repl, content)
    return new_content

def update_subscription(profile, old_email):
    """
    Update a profile subscription on campaign monitor.
    If the old email is not on CM this will not subscribe the user
    to CM.
    """
    if api_key and client_id:
        user = profile.user
        for group in profile.get_groups():
            for listmap in group.listmap_set.all():
                subscriber = Subscriber(auth, listmap.list_id, old_email)
                try:
                    subscriber.update(user.email, user.get_full_name(), [], False)
                except BadRequest, e:
                    print e
