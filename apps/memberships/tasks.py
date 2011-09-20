from datetime import datetime
from celery.task import Task
from celery.registry import tasks
from memberships.models import AppEntry, AppField, AppFieldEntry

class ImportMembershipsTask(Task):

    def run(self, app, memberships, fields, **kwargs):
        added = []
        skipped = []
        
        for membership in memberships:

            if not membership.pk:  # new membership; no pk

                membership.save()  # create pk

                # create entry
                entry = AppEntry.objects.create(
                    app = app,
                    user = membership.user,
                    entry_time = datetime.now(),
                    membership = membership,  # pk required here
                    is_renewal = membership.renewal,
                    is_approved = True,
                    decision_dt = membership.subscribe_dt,
                    judge = membership.creator,
                    creator=membership.creator,
                    creator_username=membership.creator_username,
                    owner=membership.owner,
                    owner_username=membership.owner_username,
                )

                # create entry fields
                for key, value in fields.items():

                    app_fields = AppField.objects.filter(app=app, label=key)
                    if app_fields and membership.m.get(value):

                        try:
                            value = unicode(membership.m.get(unicode(value)))
                        except (UnicodeDecodeError) as e:
                            value = ''

                        AppFieldEntry.objects.create(
                            entry=entry,
                            field=app_fields[0],
                            value=value,
                        )

                # update membership number
                if not membership.member_number:
                    membership.member_number = AppEntry.objects.count() + 1000
                    membership.save()

                # add user to group
                membership.membership_type.group.add_user(membership.user)

                added.append(membership)
            else:
                skipped.append(membership)
                
            return (memberships, added, skipped)


tasks.register(ImportMembershipsTask)
