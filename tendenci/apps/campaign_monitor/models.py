from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.utils.translation import ugettext_lazy as _
from tendenci.apps.user_groups.models import Group, GroupMembership
from tendenci.apps.forms_builder.forms.models import FormEntry
from tendenci.apps.files.models import file_directory
from tendenci.libs.boto_s3.utils import set_s3_file_permission


class ListMap(models.Model):
    group = models.ForeignKey(Group)
    # list id for campaign monitor
    list_id = models.CharField(max_length=100)
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    last_sync_dt = models.DateTimeField(null=True)

    def __unicode__(self):
        if self.group:
            return self.group.name
        return ''


class GroupQueue(models.Model):
    group = models.ForeignKey(Group)


class SubscriberQueue(models.Model):
    group = models.ForeignKey(Group)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    subscriber = models.ForeignKey(FormEntry, null=True)


class Template(models.Model):
    """
    This represents a Template in Campaign Monitor.
    """
    class Meta:
        permissions = (("view_template", _("Can view template")),)

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

    def save(self, *args, **kwargs):
        super(Template, self).save(*args, **kwargs)
        if self.html_file:
            set_s3_file_permission(self.html_file.file, public=True)
        if self.zip_file:
            set_s3_file_permission(self.zip_file.file, public=True)


class Campaign(models.Model):
    """
    This represents a Campaign. It is considered as a "Draft" if it is
    not yet sent.
    """

    class Meta:
        permissions = (("view_campaign", _("Can view campaign")),)

    STATUS_CHOICES = (
        ('S', _('Sent')),
        ('C', _('Scheduled')),
        ('D', _('Draft')),
    )

    campaign_id = models.CharField(max_length=100, unique=True)
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='D')

    #fields for sync
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=500)
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
auth = {'api_key': cm_api_key}
if cm_api_key and cm_client_id:
    from createsend import List, Client, Subscriber, BadRequest, Unauthorized, ServerError
    #CreateSend.api_key = cm_api_key

    def sync_cm_list(sender, instance=None, created=False, **kwargs):
        """Check if sync_newsletters. Do nothing if false.
            On Group Add:
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

        cl = Client(auth, cm_client_id)
        lists = cl.lists()
        list_ids = [alist.ListID for alist in lists]
        list_names = [alist.Name for alist in lists]
        list_ids_d = dict(zip(list_names, list_ids))
        list_d = dict(zip(list_ids, lists))

        if created and instance.sync_newsletters:
            if instance.name in list_names:
                list_id = list_ids_d[instance.name]

            else:
                list_id = get_or_create_cm_list(cm_client_id, instance)

            if list_id:
                # add an entry to the listmap
                listmap_insert(instance, list_id)

                # custom fields setup
                cm_list = List(auth, list_id)
                setup_custom_fields(cm_list)

        elif instance.sync_newsletters:  # update
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

            if list_id and list_id in list_ids:
                alist = list_d[list_id]
                cm_list = List(auth, list_id)
                # setup custom fields
                setup_custom_fields(cm_list)
                # if the list title doesn't match with the group name, update the list title
                if instance.name != alist.Name:
                    try:
                        # trap the error for now
                        # TODO: update only if the list title does not exist
                        # within a client.
                        cm_list.update(instance.name, "", False, "")
                    except:
                        pass

    def delete_cm_list(sender, instance=None, **kwargs):
        """Delete the list from campaign monitor
        """
        if instance:
            try:
                list_map = ListMap.objects.get(group=instance)
                list_id = list_map.list_id
                alist = List(auth, list_id)

                if alist:
                    try:
                        alist.delete()
                    except:
                        pass
                list_map.delete()

            except ListMap.DoesNotExist:
                pass

    def sync_cm_subscriber(sender, instance=None, created=False, **kwargs):
        """Subscribe the subscriber to the campaign monitor list
           Check if sync_newsletters is True. Do nothing if False.
        """
        from tendenci.apps.base.utils import validate_email
        from tendenci.apps.profiles.models import Profile

        if instance and instance.group and not instance.group.sync_newsletters:
            return

        (name, email) = get_name_email(instance)
        if email and validate_email(email):
            add_list = False
            add_subscriber = True
            list_map = None

            # Append custom fields from the profile
            profile = None
            if hasattr(instance, 'member'):
                try:
                    profile = instance.member.profile
                except Profile.DoesNotExist:
                    profile = None
            custom_data = []
            if profile:
                fields = ['city', 'state', 'zipcode', 'country',
                          'sex', 'member_number']
                for field in fields:
                    data = {}
                    data['Key'] = field
                    data['Value'] = getattr(profile, field)
                    if not data['Value']:
                        data['Clear'] = True
                    custom_data.append(data)

            try:
                list_map = ListMap.objects.get(group=instance.group)
                list_id = list_map.list_id
                alist = List(auth, list_id)

                if alist:
                    # subscriber setup
                    subscriber_obj = Subscriber(auth, list_id)

                    try:
                        list_stats = alist.stats()

                        # check if this user has already subscribed, if not, subscribe it
                        try:
                            subscriber = subscriber_obj.get(list_id, email)
                            if str(subscriber.State).lower() == 'active':
                                subscriber = subscriber_obj.update(email, name,
                                                        custom_data, True)
                                add_subscriber = False
                        except BadRequest:
                            pass
                    except Unauthorized:
                        alist = List(auth)
                        add_list = True
                    except ServerError:
                        pass
            except ListMap.DoesNotExist:
                alist = List(auth)
                add_list = True

            try:
                if add_list:
                    # this list might be deleted on campaign monitor, add it back
                    list_id = alist.create(cm_client_id, instance.group.name,
                                          "", False, "")
                    # custom fields setup
                    setup_custom_fields(alist)
                    subscriber_obj = Subscriber(auth, list_id)
                    if not list_map:
                        list_map = ListMap()
                        list_map.group = instance.group
                    list_map.list_id = list_id
                    list_map.save()

                if add_subscriber:
                    email_address = subscriber_obj.add(list_id, email, name,
                                                       custom_data, True)
            except BadRequest:
                pass

    def delete_cm_subscriber(sender, instance=None, **kwargs):
        """Delete the subscriber from the campaign monitor list
        """
        from tendenci.apps.base.utils import validate_email

        (name, email) = get_name_email(instance)
        if email and validate_email(email):
            try:
                list_map = ListMap.objects.get(group=instance.group)
                list_id = list_map.list_id
                alist = List(auth, list_id)

                if alist:
                    subscriber_obj = Subscriber(auth, list_id, email)
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
            cm_list = List(auth)
            list_id = cm_list.create(client_id, group.name, "", False, "")
        except:
            # add group to the queue for later process
            # might log exception reason in the queue
            gq = GroupQueue(group=group)
            gq.save()
            list_id = None

        return list_id

    def setup_custom_fields(cm_list):
        # create the custom fields
        profile_fields = ['city', 'state', 'zipcode', 'country', 'sex',
                            'member_number']
        cm_fields = cm_list.custom_fields()
        custom_fields = [cf.Key for cf in cm_fields]
        for field in profile_fields:
            if (u'[%s]' % field) not in custom_fields:
                cm_list.create_custom_field(field, "Text")

    def get_name_email(instance):
        email = ""
        name = ""
        if isinstance(instance, GroupMembership):
            email = instance.member.email
            name = instance.member.get_full_name()

        return (name, email)

    post_save.connect(sync_cm_list, sender=Group)
    pre_delete.connect(delete_cm_list, sender=Group)

    post_save.connect(sync_cm_subscriber, sender=GroupMembership)
    pre_delete.connect(delete_cm_subscriber, sender=GroupMembership)
