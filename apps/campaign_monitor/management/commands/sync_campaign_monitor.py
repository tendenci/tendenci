from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    """
    This script is to sync the groups and group subscribers with the campaign monitor 
    
    To run the command: python manage.py sync_campaign_monitor --verbosity 2
    """
    
    def handle(self, *args, **options):
        from user_groups.models import Group
        from subscribers.models import GroupSubscription as GS
        from campaign_monitor.models import ListMap
        from createsend import CreateSend, Client, List, Subscriber, BadRequest
        
        verbosity = 1
        if 'verbosity' in options:
            verbosity = options['verbosity']
            
        def subscribe_to_list(subscriber_obj, list_id, name, email):
            try:
                subscriber = subscriber_obj.get(list_id, email)
            except BadRequest as br:
                email_address = subscriber_obj.add(list_id, email, name, [], True)
                if verbosity >=2:
                        print "%s (%s)" % (name, email)
        
        
        api_key = getattr(settings, 'CAMPAIGNMONITOR_API_KEY', None) 
        client_id = getattr(settings, 'CAMPAIGNMONITOR_API_CLIENT_ID', None)
        CreateSend.api_key = api_key
        
        cl = Client(client_id)
        lists = cl.lists()
        list_ids = [list.ListID for list in lists]
        list_names = [list.Name for list in lists]
        list_ids_d = dict(zip(list_names, list_ids))

        groups = Group.objects.filter(status=1, status_detail='active')
        listmaps = ListMap.objects.all()
        syncd_groups = [listmap.group for listmap in listmaps]
        cm_list = List()
        
        print "Starting to sync groups with campaign monitor..."
        print
        
        for group in groups:
            if group not in syncd_groups:
                # campaing monitor requires the list title 
                if group.name in list_names:
                    list_id = list_ids_d[group.name]
                else:
                    # add group to the campaign monitor
                    list_id = cm_list.create(client_id, group.name, "", False, "")
                    print "Added group '%s' to the C.M. list." % group.name
                    print
                    
                # insert to the listmap
                list_map = ListMap(group=group,
                           list_id=list_id)
                list_map.save()
            else:
                list_map = ListMap.objects.filter(group=group)[0]
                list_id = list_map.list_id
                
            # sync subscribers in this group
            print "Subscribing users to the C.M. list '%s'..." % group.name
            members = group.members.all()
            subscriber_obj = Subscriber(list_id)
            for i, member in enumerate(members, 1):
                email = member.email
                name = member.get_full_name()
                
                subscribe_to_list(subscriber_obj, list_id, name, email)
            
            # sync subscribers in this group's subscription
            gss = GS.objects.filter(group=group)
            for gs in gss:
                form_entry = gs.subscriber
                (name, email) = form_entry.get_name_email()
                subscribe_to_list(subscriber_obj, list_id, name, email)
                    
        print 'Done'
                    
                