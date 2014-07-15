from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Converts subscribers to users, maintains group memberships, removes subscribers.
        """
        from tendenci.apps.subscribers.models import SubscriberData, GroupSubscription
        from tendenci.apps.user_groups.models import GroupMembership
        from tendenci.apps.profiles.models import Profile

        if GroupSubscription.objects.exists():
            for sub in GroupSubscription.objects.all():
                sub_email = sub.email

                if sub_email:
                    if not User.objects.filter(email=sub_email).exists():
                        print "Creating new user for group subscription %s." % sub.id
                        if len(sub_email) <= 30:
                            username = sub_email
                        else:
                            username = sub_email.split("@")[0]

                        user = User(
                            username = username,
                            email = sub_email,
                            is_active = False
                        )

                        if sub.subscriber_id:
                            user.first_name = sub.subscriber.get_first_name()
                            user.last_name = sub.subscriber.get_last_name()
                            phone = sub.subscriber.get_phone_number()
                        else:
                            if SubscriberData.objects.filter(field_label="First Name").filter(subscription_id=sub.id):
                                user.first_name = SubscriberData.objects.filter(field_label="First Name").filter(subscription_id=sub.id)[0].value
                            if SubscriberData.objects.filter(field_label="Last Name").filter(subscription_id=sub.id):
                                user.last_name = SubscriberData.objects.filter(field_label="Last Name").filter(subscription_id=sub.id)[0].value
                            if SubscriberData.objects.filter(field_label__in=["Phone", "phone", "Phone Number", "phone number", "Home Phone", "Cell Phone"]).filter(subscription_id=sub.id):
                                phone = SubscriberData.objects.filter(field_label__in=["Phone", "phone", "Phone Number", "phone number", "Home Phone", "Cell Phone"]).filter(subscription_id=sub.id)[0].value
                            else:
                                phone = ''

                        user.save()

                        profile = Profile(
                            user = user,
                            creator = user,
                            creator_username = user.username,
                            owner = user,
                            owner_username = user.username,
                            phone = phone,
                            allow_anonymous_view = False
                        )

                        profile.save()

                    else:
                        print "User with matching email found for group subscription %s."  % sub.id

                    user = User.objects.filter(email=sub_email).order_by('last_login')[0]

                    if not GroupMembership.objects.filter(group_id=sub.group_id).filter(member_id=user.id).exists():
                        print "Creating a group membership for user %s and group %s." % (user.id, sub.group_id)
                        gm = GroupMembership(
                            group_id = sub.group_id,
                            member_id = user.id,
                            role = "subscriber"
                        )
                        gm.save()
                    else:
                        print "Group membership already exists for user %s and group %s." % (user.id, sub.group_id)

                    print "Deleting group subscription %s." % sub.id
                    sub.delete()
                else:
                    print "No email field found for subscriber %s." % sub.id
        else:
            print "No group subscriptions exist."