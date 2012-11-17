from celery.registry import tasks
from celery.task import Task
from django.template.defaultfilters import slugify
from tendenci.core.exports.utils import render_csv
from tendenci.core.event_logs.models import EventLog
from tendenci.addons.memberships.importer.tasks import ImportMembershipsTask
from tendenci.addons.memberships.models import Membership, AppField

class MembershipsExportTask(Task):
    """ Export Memberships with app entry data.
    """

    def run(self, **kwargs):
        app = kwargs.pop('app')
    
        file_name = "%s.csv" % slugify(app.name)
    
        exclude_params = (
            'horizontal-rule',
            'header',
        )
    
        fields = AppField.objects.filter(app=app, exportable=True).exclude(field_type__in=exclude_params).order_by('position')

        label_list = [field.label for field in fields]
        extra_field_labels = ['User Name', 'Member Number', 'Join Date', 'Renew Date', 'Expiration Date', 'Status', 'Status Detail', 'Invoice Number', 'Invoice Amount', 'Invoice Balance']
        extra_field_names = ['user', 'member_number', 'join_dt', 'renew_dt', 'expire_dt', 'status', 'status_detail', 'invoice', 'invoice_total', 'invoice_balance']
    
        label_list.extend(extra_field_labels)
    
        data_row_list = []
        memberships = Membership.objects.filter(ma=app).exclude(status_detail='archive')
        for memb in memberships:
            data_row = []
            field_entry_d = memb.entry_items
            invoice = None
            if memb.get_entry():
                invoice = memb.get_entry().invoice
            for field in fields:
                field_name = slugify(field.label).replace('-', '_')
                value = ''
    
                if field.field_type in ['first-name', 'last-name', 'email', 'membership-type', 'payment-method', 'corporate_membership_id']:
                    if field.field_type == 'first-name':
                        value = memb.user.first_name
                    elif field.field_type == 'last-name':
                        value = memb.user.last_name
                    elif field.field_type == 'email':
                        value = memb.user.email
                    elif field.field_type == 'membership-type':
                        value = memb.membership_type.name
                    elif field.field_type == 'payment-method':
                        if memb.payment_method:
                            value = memb.payment_method.human_name
                    elif field.field_type == 'corporate_membership_id':
                        value = memb.corporate_membership_id
    
                if field_name in field_entry_d:
                    value = field_entry_d[field_name]
    
                value = value or u''
                if type(value) in (bool, int, long, None):
                    value = unicode(value)
    
                data_row.append(value)
    
            for field in extra_field_names:
    
                if field == 'user':
                    value = memb.user.username
                elif field == 'join_dt':
                    if memb.renewal:
                        value = ''
                    else:
                        value = memb.subscribe_dt
                elif field == 'renew_dt':
                    if memb.renewal:
                        value = memb.subscribe_dt
                    else:
                        value = ''
                elif field == 'expire_dt':
                    value = memb.expire_dt or 'never expire'
                elif field == 'invoice':
                    if invoice:
                        value = unicode(invoice.id)
                    else:
                        value = ""
                elif field == 'invoice_total':
                    if invoice:
                        value = unicode(invoice.total)
                    else:
                        value = ""
                elif field == 'invoice_balance':
                    if invoice:
                        value = unicode(invoice.balance)
                    else:
                        value = ""
                else:
                    value = getattr(memb, field, '')
    
                if type(value) in (bool, int, long):
                    value = unicode(value)
    
                data_row.append(value)
    
            data_row_list.append(data_row)
    
        EventLog.objects.log()
    
        return render_csv(file_name, label_list, data_row_list)
        
tasks.register(ImportMembershipsTask)
