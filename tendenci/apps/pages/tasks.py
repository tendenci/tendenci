from builtins import str
from django.db.models.fields.related import ManyToManyField, ForeignKey
from django.contrib.contenttypes.fields import GenericRelation
import celery
from tendenci.apps.exports.utils import render_csv
from tendenci.apps.pages.models import Page
from tendenci.apps.base.utils import escape_csv

class PagesExportTask(celery.Task):
    """Export Task for Celery
    This exports all active pages
    """

    def run(self, **kwargs):
        """Create the xls file"""
        fields = [
            'guid',
            'title',
            'slug',
            'header_image',
            'content',
            'view_contact_form',
            'design_notes',
            'syndicate',
            'template',
            'tags',
            'entity',
            'meta',
            'categories',
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
        ]

        file_name = 'pages.csv'

        pages = Page.objects.active()
        data_row_list = []
        for page in pages:
            # get the available fields from the model's meta
            opts = page._meta
            d = {}
            for f in opts.get_fields() + opts.many_to_many:
                if f.name in fields: # include specified fields only
                    if isinstance(f, ManyToManyField):
                        value = ["%s" % obj for obj in f.value_from_object(page)]
                    if isinstance(f, ForeignKey):
                        value = getattr(page, f.name)
                    if isinstance(f, GenericRelation):
                        generics = f.value_from_object(page).all()
                        value = ["%s" % obj for obj in generics]
                        value = ', '.join(value)
                    else:
                        value = f.value_from_object(page)
                    d[f.name] = value

            # append the accumulated values as a data row
            # keep in mind the ordering of the fields
            data_row = []
            for field in fields:
                # clean the derived values into unicode
                value = str(d[field]).rstrip()
                value = escape_csv(value)
                data_row.append(value)

            data_row_list.append(data_row)

        return render_csv(file_name, fields, data_row_list)
