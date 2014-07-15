import os
from datetime import datetime

from django.forms.models import model_to_dict
from django.db.models.fields import DateTimeField
from django.db.models.fields.related import ManyToManyField, ForeignKey
from django.contrib.contenttypes import generic
from celery.task import Task
from tendenci.core.perms.models import TendenciBaseModel
from tendenci.core.exports.utils import render_csv

class InvoiceExportTask(Task):
    """Export Task for Celery
    This exports the entire queryset of a given TendenciBaseModel.
    """

    def run(self, model, start_dt, end_dt, file_name, **kwargs):
        """Create the xls file"""
        fields = (
            'id',
            'guid',
            'object_type',
            'object_id',
            'title',
            'tender_date',
            'bill_to',
            'bill_to_first_name',
            'bill_to_last_name',
            'bill_to_company',
            'bill_to_address',
            'bill_to_city',
            'bill_to_state',
            'bill_to_zip_code',
            'bill_to_country',
            'bill_to_phone',
            'bill_to_fax',
            'bill_to_email',
            'ship_to',
            'ship_to_first_name',
            'ship_to_last_name',
            'ship_to_company',
            'ship_to_address',
            'ship_to_city',
            'ship_to_state',
            'ship_to_zip_code',
            'ship_to_country',
            'ship_to_phone',
            'ship_to_fax',
            'ship_to_email',
            'ship_to_address_type',
            'receipt',
            'gift',
            'arrival_date_time',
            'greeting',
            'instructions',
            'po',
            'terms',
            'due_date',
            'ship_date',
            'ship_via',
            'fob',
            'project',
            'other',
            'message',
            'subtotal',
            'shipping',
            'shipping_surcharge',
            'box_and_packing',
            'tax_exempt',
            'tax_exemptid',
            'tax_rate',
            'taxable',
            'tax',
            'variance',
            'discount_amount',
            'total',
            'payments_credits',
            'balance',
            'disclaimer',
            'variance_notes',
            'admin_notes',
            'create_dt',
            'update_dt',
            'creator',
            'creator_username',
            'owner',
            'owner_username',
            'status_detail',
            'status',
        )

        start_dt_date = datetime.strptime(start_dt, "%Y-%m-%d")
        end_dt_date = datetime.strptime(end_dt, "%Y-%m-%d")

        items = model.objects.filter(status=True, tender_date__gte=start_dt_date, tender_date__lte=end_dt_date)
        data_row_list = []
        for item in items:
            # get the available fields from the model's meta
            opts = item._meta
            d = {}
            for f in opts.fields + opts.many_to_many:
                if f.name in fields:  # include specified fields only
                    if isinstance(f, ManyToManyField):
                        value = ["%s" % obj for obj in f.value_from_object(item)]
                    if isinstance(f, ForeignKey):
                        value = getattr(item, f.name)
                    if isinstance(f, generic.GenericRelation):
                        generics = f.value_from_object(item).all()
                        value = ["%s" % obj for obj in generics]
                    if isinstance(f, DateTimeField):
                        if f.value_from_object(item):
                            value = f.value_from_object(item).strftime("%Y-%m-%d %H:%M")
                    else:
                        value = f.value_from_object(item)
                    d[f.name] = value

            # append the accumulated values as a data row
            # keep in mind the ordering of the fields
            data_row = []
            for field in fields:
                # clean the derived values into unicode
                value = unicode(d[field]).rstrip()
                data_row.append(value)

            data_row_list.append(data_row)

        return render_csv(file_name, fields, data_row_list)
