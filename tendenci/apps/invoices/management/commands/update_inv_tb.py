
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        # command to run: python manage.py update_inv_tb
        """
        This command will:
            1) add the object_type field
            2) populate the object_type field based on the content in invoice_object_type
            3) drop field invoice_object_type
            4) rename field invoice_object_type_id to object_id
        """
        from django.db import connection, transaction
        from django.contrib.contenttypes.models import ContentType
        cursor = connection.cursor()

        # add the object_type field
        cursor.execute("ALTER TABLE invoices_invoice ADD object_type_id int AFTER guid")
        transaction.commit_unless_managed()
        print("Field object_type_id - Added")

        # assign content type to object_type based on the invoice_object_type
        try:
            ct_make_payment = ContentType.objects.get(app_label='make_payments', model='MakePayment')
        except:
            ct_make_payment = None
        try:
            ct_donation = ContentType.objects.get(app_label='donations', model='Donation')
        except:
            ct_donation = None
        try:
            ct_job = ContentType.objects.get(app_label='jobs', model='Job')
        except:
            ct_job = None
        try:
            ct_directory = ContentType.objects.get(app_label='directories', model='Directory')
        except:
            ct_directory = None
        try:
            ct_event_registration = ContentType.objects.get(app_label='events', model='Registration')
        except:
            ct_event_registration = None
        try:
            ct_corp_memb = ContentType.objects.get(app_label='corporate_memberships', model='CorporateMembership')
        except:
            ct_corp_memb = None

        if ct_make_payment:
            cursor.execute("""UPDATE invoices_invoice
                                SET object_type_id=%s
                                WHERE (invoice_object_type='make_payment'
                                OR invoice_object_type='makepayments') """, [ct_make_payment.id])
            transaction.commit_unless_managed()

        if ct_donation:
            cursor.execute("""UPDATE invoices_invoice
                                SET object_type_id=%s
                                WHERE (invoice_object_type='donation'
                                OR invoice_object_type='donations')  """, [ct_donation.id])
            transaction.commit_unless_managed()

        if ct_job:
            cursor.execute("""UPDATE invoices_invoice
                                SET object_type_id=%s
                                WHERE (invoice_object_type='job'
                                OR invoice_object_type='jobs')  """, [ct_job.id])
            transaction.commit_unless_managed()

        if ct_directory:
            cursor.execute("""UPDATE invoices_invoice
                                SET object_type_id=%s
                                WHERE (invoice_object_type='directory'
                                OR invoice_object_type='directories') """, [ct_directory.id])
            transaction.commit_unless_managed()

        if ct_event_registration:
            cursor.execute("""UPDATE invoices_invoice
                                SET object_type_id=%s
                                WHERE (invoice_object_type='event_registration'
                                OR invoice_object_type='calendarevents') """,  [ct_event_registration.id])
        if ct_corp_memb:
            cursor.execute("""UPDATE invoices_invoice
                                SET object_type_id=%s
                                WHERE (invoice_object_type='corporate_membership'
                                OR invoice_object_type='corporatememberships')  """,  [ct_corp_memb.id])
            transaction.commit_unless_managed()

        print("Field object_type_id - Populated")

        # drop field invoice_object_type
        cursor.execute("ALTER TABLE invoices_invoice DROP invoice_object_type")
        transaction.commit_unless_managed()

        print("Field invoice_object_type - Dropped")

        # rename invoice_object_type_id to object_id
        cursor.execute("ALTER TABLE invoices_invoice CHANGE invoice_object_type_id object_id int")
        transaction.commit_unless_managed()
        print("Renamed invoice_object_type to object_id")

        print("done")
