from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from user_groups.models import Group, GroupMembership
from forms_builder.forms.models import FormEntry
from subscribers.models import GroupSubscription
from files.models import file_directory

class ListMap(models.Model):
    group = models.ForeignKey(Group)
    # list id for campaign monitor
    list_id = models.CharField(max_length=100)
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    last_sync_dt = models.DateTimeField(null=True)
    
    def __unicode__(self):
        return self.group.name
    
class GroupQueue(models.Model):
    group = models.ForeignKey(Group)
    
class SubscriberQueue(models.Model):
    group = models.ForeignKey(Group)
    user = models.ForeignKey(User, null=True)
    subscriber = models.ForeignKey(FormEntry, null=True)
    
class Template(models.Model):
    """
    This represents a Template in Campaign Monitor.
    """
    class Meta:
        permissions = (("view_template","Can view template"),)
    
    template_id = models.CharField(max_length=100, unique=True, null=True)
    name = models.CharField(max_length=100)
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    
    #get only
    cm_preview_url = models.URLField(null=True)
    cm_screenshot_url = models.URLField(null=True)
    
    #post only
    html_file = models.FileField(upload_to=file_directory, null=True)
    zip_file = models.FileField(upload_to=file_directory, null=True)
    
    @property
    def content_type(self):
        return 'template'
    
    @models.permalink
    def get_absolute_url(self):
        return ("campaign_monitor.template_view", [self.template_id])
    
    @models.permalink
    def get_html_url(self):
        return ("campaign_monitor.template_html", [self.template_id])
    
    @models.permalink
    def get_html_original_url(self):
        return ("campaign_monitor.template_html_original", [self.template_id])
    
    @models.permalink
    def get_render_url(self):
        return ("campaign_monitor.template_render", [self.template_id])
    
    @models.permalink
    def get_text_url(self):
        return ("campaign_monitor.template_text", [self.template_id])
    
    def get_zip_url(self):
        if self.zip_file:
            return self.zip_file.url
        return ''
        
    def get_media_url(self):
        if self.zip_file:
            return "%scampaign_monitor/%s" % (settings.MEDIA_URL, self.template_id)
        return ''
        
    def __unicode__(self):
        return self.name
    
class Campaign(models.Model):
    """
    This represents a Campaign. It is considered as a "Draft" if it is 
    not yet sent.
    """
    
    class Meta:
        permissions = (("view_campaign","Can view campaign"),)
    
    STATUS_CHOICES = (
        ('S','Sent'),
        ('C', 'Scheduled'),
        ('D', 'Draft'),
    )
    
    campaign_id = models.CharField(max_length=100, unique=True)
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='D')
    
    #fields for sync
    name = models.CharField(max_length=100)
    subject =  models.CharField(max_length=100)
    lists = models.ManyToManyField(ListMap)
    
    #fields for sent campaigns
    sent_date = models.DateTimeField(null=True, blank=True)
    web_version_url = models.URLField(null=True, blank=True)
    total_recipients = models.IntegerField(default=0)
    
    #fields for scheduled campaigns
    scheduled_date = models.DateTimeField(null=True, blank=True)
    scheduled_time_zone = models.CharField(max_length=100, null=True, blank=True)
    preview_url = models.URLField(null=True, blank=True)
    
    #fields for post only
    from_name = models.CharField(max_length=100, null=True, blank=True)
    from_email = models.EmailField(null=True, blank=True)
    reply_to = models.EmailField(null=True, blank=True)
    template = models.ForeignKey(Template, null=True, blank=True)
    
    @models.permalink
    def get_absolute_url(self):
        return ("campaign_monitor.campaign_view", [self.campaign_id])
        
    def __unicode__(self):
        return self.name

# create post_save and pre_delete signals to sync with campaign monitor
# http://www.campaignmonitor.com/api/getting-started/
# http://tendenci.createsend.com/subscribers/
# https://github.com/campaignmonitor/createsend-python/blob/master/createsend/list.py
 
cm_api_key = getattr(settings, 'CAMPAIGNMONITOR_API_KEY', None) 
cm_client_id = getattr(settings, 'CAMPAIGNMONITOR_API_CLIENT_ID', None)
if cm_api_key and cm_client_id:
    from createsend import CreateSend, List, Client, Subscriber, BadRequest, Unauthorized
    CreateSend.api_key = cm_api_key
    
    def sync_cm_list(sender, instance=None, created=False, **kwargs):
        """On Group Add:
                if group name does not exist on C. M,
                    add a list to C. M.
                add an entry to listmap
                
            On Group Edit:
                if group exists on C. M.,
                    if list.name <> group.name,
                        update list name
                else:
                    add a list on C. M.
                    add an entry to listmap
        """
        
        cl = Client(cm_client_id)
        lists = cl.lists()
        list_ids = [list.ListID for list in lists]
        list_names = [list.Name for list in lists]
        list_ids_d = dict(zip(list_names, list_ids))
        list_d = dict(zip(list_ids, lists))
        
        if created:
            if instance.name in list_names:
                list_id = list_ids_d[instance.name]
                
            else:
                list_id = get_or_create_cm_list(cm_client_id, instance)
            
            if list_id:
                # add an entry to the listmap
                listmap_insert(instance, list_id)
                
            
        else:   # update
            try:
                # find the entry in the listmap
                list_map = ListMap.objects.get(group=instance)
                list_id = list_map.list_id
            except ListMap.DoesNotExist:
                if instance.name in list_names:
                    list_id = list_ids_d[instance.name]
                else:
                    # hasn't be created on C. M. yet. create one
                    list_id = get_or_create_cm_list(cm_client_id, instance)
                        
                  
                if list_id:  
                    listmap_insert(instance, list_id)
                    
            
            # if the list title doesn't match with the group name, update the list title
            if list_id and list_id in list_ids:
                list = list_d[list_id]
                if instance.name != list.Name:
                    list = List(list_id)
                    list.update(instance.name, "", False, "")
                        

    def delete_cm_list(sender, instance=None, **kwargs):
        """Delete the list from campaign monitor
        """
        if instance:
            try:
                list_map = ListMap.objects.get(group=instance)
                list_id = list_map.list_id
                list = List(list_id)
                
                if list:
                    try:
                        list.delete()
                    except:
                        pass
                list_map.delete()
                
            except ListMap.DoesNotExist:
                pass
            
    def sync_cm_subscriber(sender, instance=None, created=False, **kwargs):
        """Subscribe the subscriber to the campaign monitor list
        """
        (name, email) = get_name_email(instance)
            
        if email:
            add_list = True
            add_subscriber = True
            list_map = None
                
            try:
                list_map = ListMap.objects.get(group=instance.group)
                list_id = list_map.list_id
                list = List(list_id)
                
                if list:
                    subscriber_obj = Subscriber(list_id)
                    
                    try:
                        list_stats = list.stats()
                        #print 'number active:',  list_stats.TotalActiveSubscribers
                        add_list = False            # at this stage, we're sure the list is ON the C. M.
                    
                        # check if this user has already subscribed, if not, subscribe it
                        try:
                            subscriber = subscriber_obj.get(list_id, email)
                            if str(subscriber.State).lower == 'active':
                                add_subscriber = False
                        except BadRequest as br:
                            pass
                    except Unauthorized as e:
                        list = List()
            except ListMap.DoesNotExist:
                list = List()
                    
            if add_list:
                # this list might be deleted on campaign monitor, add it back
                list_id = list.create(cm_client_id, instance.group.name, "", False, "")
                subscriber_obj = Subscriber(list_id)
                if not list_map:
                    list_map = ListMap()
                    list_map.group = instance.group
                list_map.list_id = list_id
                list_map.save()
                    
            if add_subscriber:
                email_address = subscriber_obj.add(list_id, email, name, [], True)
                
            
    
    def delete_cm_subscriber(sender, instance=None, **kwargs):
        """Delete the subscriber from the campaign monitor list
        """
        (name, email) = get_name_email(instance)
        
        if email:
            try:
                list_map = ListMap.objects.get(group=instance.group)
                list_id = list_map.list_id
                list = List(list_id)
                
                if list:
                    subscriber_obj = Subscriber(list_id, email)
                    try:
                        subscriber_obj.unsubscribe()
                    except:
                        pass
                   
            except ListMap.DoesNotExist:
                pass
            
    def listmap_insert(group, list_id, **kwargs):
        """Add an entry to the listmap
        """
        list_map = ListMap(group=group,
                           list_id=list_id)
        list_map.save()
        
    def get_or_create_cm_list(client_id, group):
        """Get or create the list on compaign monitor
        """
        try:
            # add the list with the group name to campaign monitor
            cm_list = List()
            list_id = cm_list.create(client_id, group.name, "", False, "")
        except:
            # add group to the queue for later process
            # might log exception reason in the queue
            gq = GroupQueue(group=group)
            gq.save()
            list_id = None
            
        return list_id
            
    def get_name_email(instance):
        email = ""
        name = ""
        if isinstance(instance, GroupMembership):
            email = instance.member.email
            name = instance.member.get_full_name()
        elif isinstance(instance, GroupSubscription):
            form_entry = instance.subscriber
            (name, email) = form_entry.get_name_email()
                    
        return (name, email)
            
        
            
    post_save.connect(sync_cm_list, sender=Group)   
    pre_delete.connect(delete_cm_list, sender=Group)
    
    post_save.connect(sync_cm_subscriber, sender=GroupMembership)   
    pre_delete.connect(delete_cm_subscriber, sender=GroupMembership)
    
    post_save.connect(sync_cm_subscriber, sender=GroupSubscription)   
    pre_delete.connect(delete_cm_subscriber, sender=GroupSubscription)
    
    
    
