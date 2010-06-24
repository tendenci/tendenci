import uuid
from django.db import models

from perms.models import TendenciBaseModel
from perms.utils import is_admin

class Email(TendenciBaseModel):
    guid = models.CharField(max_length=50)
    priority = models.IntegerField(default=0)
    subject =models.CharField(max_length=255)
    body = models.TextField()
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
    
    def send(self):
        from django.core.mail.message import EmailMessage
        recipient_list = []
        recipient_bcc_list = []
        if self.recipient:
            recipient_list = self.recipient.split(',')
            recipient_list = [recipient.strip() for recipient in recipient_list \
                              if recipient.strip() <> '']
        if self.recipient_cc:
            recipient_cc_list = self.recipient_cc.split(',')
            recipient_cc_list = [recipient_cc.strip() for recipient_cc in recipient_cc_list if \
                                  recipient_cc.strip() <> '']
            recipient_list += recipient_cc_list
        if self.recipient_bcc:
            recipient_bcc_list = self.recipient_bcc.split(',')
            recipient_bcc_list = [recipient_bcc.strip() for recipient_bcc in recipient_bcc_list if \
                                   recipient_bcc.strip() <> '']
        if recipient_list or recipient_bcc_list:
            msg = EmailMessage(self.subject,
                               self.body,
                               self.sender,
                               recipient_list,
                               recipient_bcc_list,
                               headers={'Reply-To':self.reply_to,
                                        'content_type':self.content_type} )
            msg.send(fail_silently=False)
    
    def save(self, user=None):
        if not self.id:
            self.guid = str(uuid.uuid1())
            if user and user.id:
                self.creator=user
                self.creator_username=user.username
        if user and user.id:
            self.owner=user
            self.owner_username=user.username
            
        super(self.__class__, self).save()
        
    # if this email allows view by user2_compare
    def allow_view_by(self, user2_compare):
        boo = False
       
        if is_admin(user2_compare):
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
        if is_admin(user2_compare):
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
            