import os
from django.forms.models import model_to_dict
from django.db.models.fields import DateTimeField
from django.db.models.fields.related import ManyToManyField, ForeignKey
from django.contrib.contenttypes import generic
from celery.task import Task
from tendenci.core.perms.models import TendenciBaseModel
from tendenci.core.exports.utils import render_csv

class TendenciExportTask(Task):
    """Export Task for Celery
    This exports the entire queryset of a given TendenciBaseModel.
    """

    def run(self, model, fields, file_name, **kwargs):
        """Create the xls file"""
        if issubclass(model, TendenciBaseModel):
            fields = fields + (
                'allow_anonymous_view',
                'allow_user_view',
                'allow_member_view',
                'allow_user_edit',
                'allow_member_edit',
                'create_dt',
                'update_dt',
                'creator',
                'creator_username',
                'owner',
                'owner_username',
                'status',
                'status_detail',
            )

        items = model.objects.filter(status=True)
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
