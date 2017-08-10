import uuid
import copy
from django.db import models
from django.db.models import Q

from django.core.mail.message import EmailMessage
from django.conf import settings
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.libs.tinymce import models as tinymce_models
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.email_blocks.models import EmailBlock


class Email(TendenciBaseModel):

    CONTENT_TYPE_HTML = 'text/html'
    CONTENT_TYPE_TEXT = 'text'

    CONTENT_TYPE_CHOICES = (
        (CONTENT_TYPE_HTML, 'text/html'),
        (CONTENT_TYPE_TEXT, 'text'),
    )   

    guid = models.CharField(max_length=50)
    priority = models.IntegerField(default=0)
    subject = models.CharField(max_length=255)
    body = tinymce_models.HTMLField()
    # body = models.TextField()
    sender = models.CharField(max_length=255)
    sender_display = models.CharField(max_length=255)
    reply_to = models.CharField(max_length=255)
    recipient = models.CharField(max_length=255, blank=True, default='')
    recipient_dispaly = models.CharField(max_length=255, blank=True, default='')
    recipient_cc = models.CharField(max_length=255, blank=True, default='')
    recipient_cc_display = models.CharField(max_length=255, blank=True, default='')
    recipient_bcc = models.CharField(max_length=255, blank=True, default='')
    attachments = models.CharField(max_length=500, blank=True, default='')
    content_type = models.CharField(max_length=255, default=CONTENT_TYPE_HTML, choices=CONTENT_TYPE_CHOICES)

    # create_dt = models.DateTimeField(auto_now_add=True)
    # status = models.NullBooleanField(default=True, choices=((True,'Active'),(False,'Inactive'),))

    class Meta:
        app_label = 'emails'


    @models.permalink
    def get_absolute_url(self):
        return ("email.view", [self.pk])

    def __unicode__(self):
        return self.subject
    
    @staticmethod
    def is_blocked(email_to_test):
        if not email_to_test or not '@' in email_to_test:
            return False
        
        email_to_test = email_to_test.lower()
        email_domain = email_to_test.split('@')[1]
        return EmailBlock.objects.filter(Q(email=email_to_test) | Q(email_domain=email_domain)
                                         ).exists()
        

    def send(self, fail_silently=False, **kwargs):
        recipient_list = []
        recipient_bcc_list = []
        headers = kwargs.get('headers', {})
        attachments = kwargs.get('attachments', [])

        if isinstance(self.recipient, basestring):
            recipient_list = self.recipient.split(',')
            recipient_list = [recipient.strip() for recipient in recipient_list \
                              if recipient.strip() != '']
        else:
            recipient_list = list(self.recipient)
        if isinstance(self.recipient_cc, basestring):
            recipient_cc_list = self.recipient_cc.split(',')
            recipient_cc_list = [recipient_cc.strip() for recipient_cc in recipient_cc_list if \
                                  recipient_cc.strip() != '']
            recipient_list += recipient_cc_list
        else:
            recipient_list += list(self.recipient_cc)
        if isinstance(self.recipient_bcc, basestring):
            recipient_bcc_list = self.recipient_bcc.split(',')
            recipient_bcc_list = [recipient_bcc.strip() for recipient_bcc in recipient_bcc_list if \
                                   recipient_bcc.strip() != '']
        else:
            recipient_bcc_list = list(self.recipient_bcc)

        if self.reply_to:
            headers['Reply-To'] = self.reply_to
        if not self.sender:
            self.sender = get_setting('site', 'global', 'siteemailnoreplyaddress') or settings.DEFAULT_FROM_EMAIL
        if self.sender_display:
            # Add quotes around display name to prevent errors on sending
            # When display name contains comma or other control characters,
            headers['From'] = '"%s"<%s>' % (self.sender_display, self.sender)
        if self.priority and self.priority == 1:
            headers['X-Priority'] = '1'
            headers['X-MSMail-Priority'] = 'High'

        # remove blocked from recipient_list and recipient_bcc_list
        temp_recipient_list = copy.copy(recipient_list)
        for e in temp_recipient_list:
            if self.is_blocked(e):
                recipient_list.remove(e)
        temp_recipient_bcc_list = copy.copy(recipient_bcc_list)
        for e in temp_recipient_bcc_list:
            if self.is_blocked(e):
                recipient_bcc_list.remove(e)

        if recipient_list or recipient_bcc_list:
            msg = EmailMessage(self.subject,
                               self.body,
                               self.sender,
                               recipient_list,
                               recipient_bcc_list,
                               headers=headers,
                               connection=kwargs.get('connection', None))
            if self.content_type == 'html' or self.content_type == self.CONTENT_TYPE_HTML:
                msg.content_subtype = 'html'
            if attachments:
                msg.attachments = attachments
            msg.send(fail_silently=fail_silently)

    def save(self, user=None, *args, **kwargs):
        if not self.id:
            self.guid = uuid.uuid1()
            if user and not user.is_anonymous():
                self.creator = user
                self.creator_username = user.username
        if user and not user.is_anonymous():
            self.owner = user
            self.owner_username = user.username

        super(Email, self).save(*args, **kwargs)

    # if this email allows view by user2_compare
    def allow_view_by(self, user2_compare):
        boo = False

        if user2_compare.profile.is_superuser:
            boo = True
        else:
            if user2_compare == self.creator or user2_compare == self.owner:
                if self.status:
                    boo = True
            else:
                if user2_compare.has_perm('emails.view_email', self):
                    if self.status == 1 and self.status_detail == 'active':
                        boo = True
        return boo

    # if this email allows edit by user2_compare
    def allow_edit_by(self, user2_compare):
        boo = False
        if user2_compare.profile.is_superuser:
            boo = True
        else:
            if user2_compare == self.user:
                boo = True
            else:
                if user2_compare == self.creator or user2_compare == self.owner:
                    if self.status:
                        boo = True
                else:
                    if user2_compare.has_perm('emails.edit_email', self):
                        if self.status:
                            boo = True
        return boo


    def template_body(self, email_d):
        """
            build the email body from the template and variables passed in by a dictionary
        """
        import os.path
        from django.template.loader import render_to_string

        template = email_d.get('template_path_name', '')

        # check if this template exists
        boo = False
        for dir in settings.TEMPLATE_DIRS:
            if os.path.isfile(os.path.join(dir, template)):
                boo = True
                break

        if not boo:
            # log an event

            # notify admin of missing template

            pass
        else:
            self.body = render_to_string(template)
            for key in email_d.keys():
                # need to convert [blah] to %5Bblah%5D for replace line
                tmp_value = "%5B" + key[1:-1] + "%5D"
                if email_d[key] != None:
                    self.body = self.body.replace(key, email_d[key])
                    self.body = self.body.replace(tmp_value, email_d[key])
                else:
                    self.body = self.body.replace(key, '')
                    self.body = self.body.replace(tmp_value, '')

        return boo
