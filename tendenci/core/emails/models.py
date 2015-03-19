import uuid
from django.db import models

from django.core.mail.message import EmailMessage
from django.conf import settings
from tendenci.core.perms.models import TendenciBaseModel
from tinymce import models as tinymce_models
from tendenci.core.site_settings.utils import get_setting

class Email(TendenciBaseModel):
    guid = models.CharField(max_length=50)
    priority = models.IntegerField(default=0)
    subject =models.CharField(max_length=255)
    body = tinymce_models.HTMLField()
    #body = models.TextField()
    sender = models.CharField(max_length=255)
    sender_display = models.CharField(max_length=255)
    reply_to = models.CharField(max_length=255)
    recipient = models.CharField(max_length=255, blank=True, default='')
    recipient_dispaly = models.CharField(max_length=255, blank=True, default='')
    recipient_cc = models.CharField(max_length=255, blank=True, default='')
    recipient_cc_display = models.CharField(max_length=255, blank=True, default='')
    recipient_bcc = models.CharField(max_length=255, blank=True, default='')
    attachments = models.CharField(max_length=500, blank=True, default='')
    content_type = models.CharField(max_length=255, default='text/html', choices=(('text/html','text/html'),('text','text'),))

    #create_dt = models.DateTimeField(auto_now_add=True)
    #status = models.BooleanField(default=True, choices=((True,'Active'),(False,'Inactive'),))

    @models.permalink
    def get_absolute_url(self):
        return ("email", [self.pk])

    def __unicode__(self):
        return self.subject

    def send(self, fail_silently=False, **kwargs):
        recipient_list = []
        recipient_bcc_list = []
        headers = kwargs.get('headers', {})
        attachments = kwargs.get('attachments', [])

        if isinstance(self.recipient, basestring):
            recipient_list = self.recipient.split(',')
            recipient_list = [recipient.strip() for recipient in recipient_list \
                              if recipient.strip() <> '']
        else:
            recipient_list = list(self.recipient)
        if isinstance(self.recipient_cc, basestring):
            recipient_cc_list = self.recipient_cc.split(',')
            recipient_cc_list = [recipient_cc.strip() for recipient_cc in recipient_cc_list if \
                                  recipient_cc.strip() <> '']
            recipient_list += recipient_cc_list
        else:
            recipient_list += list(self.recipient_cc)
        if isinstance(self.recipient_bcc, basestring):
            recipient_bcc_list = self.recipient_bcc.split(',')
            recipient_bcc_list = [recipient_bcc.strip() for recipient_bcc in recipient_bcc_list if \
                                   recipient_bcc.strip() <> '']
        else:
            recipient_bcc_list = list(self.recipient_bcc)

        if self.reply_to:
            headers['Reply-To'] = self.reply_to
        if not self.sender:
            self.sender = get_setting('site', 'global', 'siteemailnoreplyaddress') or settings.DEFAULT_FROM_EMAIL
        if self.sender_display:
            headers['From'] = '%s<%s>' % (self.sender_display, self.sender)
        if self.priority and self.priority == 1:
            headers['X-Priority'] = '1'
            headers['X-MSMail-Priority'] = 'High'

        if recipient_list or recipient_bcc_list:
            msg = EmailMessage(self.subject,
                               self.body,
                               self.sender,
                               recipient_list,
                               recipient_bcc_list,
                               headers=headers,
                               connection=kwargs.get('connection', None))
            if self.content_type == 'html' or self.content_type == 'text/html':
                msg.content_subtype = 'html'
            if attachments:
                msg.attachments = attachments
            msg.send(fail_silently=fail_silently)

    def save(self, user=None):
        if not self.id:
            self.guid = uuid.uuid1()
            if user and not user.is_anonymous():
                self.creator=user
                self.creator_username=user.username
        if user and not user.is_anonymous():
            self.owner=user
            self.owner_username=user.username

        super(Email, self).save()

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
                    if self.status == 1 and self.status_detail=='active':
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
                if email_d[key] <> None:
                    self.body = self.body.replace(key, email_d[key])
                    self.body = self.body.replace(tmp_value, email_d[key])
                else:
                    self.body = self.body.replace(key, '')
                    self.body = self.body.replace(tmp_value, '')

        return boo
