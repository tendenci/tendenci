
from csv import writer
from datetime import datetime
from mimetypes import guess_type


from django.conf import settings
from django.conf.urls import patterns, url
from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.site_settings.utils import get_setting

from tendenci.apps.forms_builder.forms.models import Form, Field, FormEntry, FieldEntry, Pricing
from tendenci.apps.forms_builder.forms.forms import FormAdminForm, FormForField, PricingForm

import os
import mimetypes


class PricingAdminForm(PricingForm):
    class Meta:
        model = Pricing
        exclude = ('billing_period',
                   'billing_frequency',
                   'num_days',
                   'due_sore',
                  )


class PricingAdmin(admin.StackedInline):
    model = Pricing
    form = PricingAdminForm
    extra = 0
    template = 'admin/forms/edit_inline/stacked.html'


class FieldAdminForm(FormForField):
    class Meta:
        model = Field
        # django 1.8 requires either 'fields' or 'exclude' for ModelForm
        exclude = ()


class FieldAdmin(admin.TabularInline):
    model = Field
    form = FieldAdminForm
    extra = 0
    ordering = ("position",)


class FormAdmin(TendenciBaseModelAdmin):

    inlines = (PricingAdmin, FieldAdmin,)
    list_display = ("title", "intro", "email_from", "email_copies",
        "admin_link_export", 'export_all_link', "admin_link_view")
    list_display_links = ("title",)
#    list_filter = ("status",)
    search_fields = ("title", "intro", "response", "email_from",
        "email_copies")
#    radio_fields = {"status": admin.HORIZONTAL}
    prepopulated_fields = {'slug': ['title']}

    if not get_setting('module', 'recurring_payments', 'enabled'):
        payment_fields = ("custom_payment", "payment_methods")
    else:
        payment_fields = ("custom_payment", 'recurring_payment', "payment_methods")

    position_fields = ("intro_position", "fields_position", "pricing_position")
    section_name_fields = ("intro_name", "fields_name", "pricing_name")

    fieldsets = (
        (None, {"fields": ("title", "slug", "intro", "response", "completion_url", "template")}),
        (_("Email"), {"fields": ('subject_template', "email_from", "email_copies", "send_email", "email_text")}),
        (_('Permissions'), {'fields': ('allow_anonymous_view',)}),
        (_('Advanced Permissions'), {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        (_('Publishing Status'), {'fields': (
            'status_detail',
        )}),
        (_("Payment"), {"fields": payment_fields}),
        (_("Section Positions"), {"fields": position_fields,
                                  "description": _("Please select the order in which you would like the Intro paragraph, the fields (name, date, address, etc) and the pricing options to appear on your finished form. Example: If you want the paragraph at the top, position the 'Intro' to the first position.")}),
        (_("Section Names"), {"fields": section_name_fields,
                              "description": _("Label the section names to meet the needs of your form. Examples for the pricing section would be: Pricing, Costs, Ticket Prices, Additional Costs, Service Fees and text of that nature.")}),
    )

    form = FormAdminForm

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.11.0/jquery-ui.min.js',
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
            '%sjs/admin/form-fields-inline-ordering.js' % settings.STATIC_URL,
            '%sjs/admin/form-field-dynamic-hiding.js' % settings.STATIC_URL,
            '%sjs/admin/form-position.js' % settings.STATIC_URL,
            '%sjs/admin/tax_fields.js' % settings.STATIC_URL,
        )
        css = {'all': ['%scss/admin/dynamic-inlines-with-sort.css' % settings.STATIC_URL], }

    def export_all_link(self, obj):
        link = '-----'
        if obj.has_files():
            link = '<a href="%s" title="Export all">Export entries (including uploaded files)</a>' % reverse('form_entries_export_full', args=[obj.pk])
        return link
    export_all_link.allow_tags = True
    export_all_link.short_description = ''


    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, unquote(object_id))

        #check if the form has file fields
        extra_context = extra_context or {}
        extra_context['has_files'] = obj.has_files()

        for inline_class in self.inlines:
            if inline_class.model == Field:
                if obj.fields_name:
                    inline_class.verbose_name = obj.fields_name
                    inline_class.verbose_name_plural = obj.fields_name
            elif inline_class.model == Pricing:
                inline_class.verbose_name = obj.pricing_name
                inline_class.verbose_name_plural = obj.pricing_name

        return super(FormAdmin, self).change_view(request, object_id, form_url, extra_context)

    def get_urls(self):
        """
        Add the export view to urls.
        """
        urls = super(FormAdmin, self).get_urls()
        extra_urls = patterns("",
            url("^export/(?P<form_id>\d+)/$",
                self.admin_site.admin_view(self.export_view),
                name="forms_form_export"),
            url("^file/(?P<field_entry_id>\d+)/$",
                self.admin_site.admin_view(self.file_view),
                name="forms_form_file"),
        )
        return extra_urls + urls

    def export_view(self, request, form_id):
        """
        Output a CSV file to the browser containing the entries for the form.
        """
        form = get_object_or_404(Form, id=form_id)
        response = HttpResponse(content_type="text/csv")
        csvname = "%s-%s.csv" % (form.slug, slugify(datetime.now().ctime()))
        response["Content-Disposition"] = "attachment; filename=%s" % csvname
        csv = writer(response)
        # Write out the column names and store the index of each field
        # against its ID for building each entry row. Also store the IDs of
        # fields with a type of FileField for converting their field values
        # into download URLs.
        columns = []
        field_indexes = {}
        file_field_ids = []
        for field in form.fields.all().order_by('position', 'id'):
            columns.append(field.label.encode("utf-8"))
            field_indexes[field.id] = len(field_indexes)
            if field.field_type == "FileField":
                file_field_ids.append(field.id)
        entry_time_name = FormEntry._meta.get_field("entry_time").verbose_name
        columns.append(unicode(entry_time_name))
        if form.custom_payment:
            columns.append(unicode("Pricing"))
            columns.append(unicode("Price"))
            columns.append(unicode("Payment Method"))
        csv.writerow(columns)
        # Loop through each field value order by entry, building up each
        # entry as a row.
        entries = FormEntry.objects.filter(form=form).order_by('pk')
        for entry in entries:
            values = FieldEntry.objects.filter(entry=entry)
            row = [""] * len(columns)
            entry_time = entry.entry_time.strftime("%Y-%m-%d %H:%M:%S")

            if form.custom_payment:
                if entry.pricing:
                    row[-4] = entry_time
                    row[-3] = entry.pricing.label
                    if not entry.pricing.price:
                        row[-2] = entry.custom_price
                    else:
                        row[-2] = entry.pricing.price
                row[-1] = entry.payment_method
            else:
                row[-1] = entry_time

            for field_entry in values:
                value = field_entry.value.encode("utf-8")
                # Create download URL for file fields.
                if field_entry.field_id in file_field_ids:
                    url = reverse("admin:forms_form_file", args=(field_entry.id,))
                    value = request.build_absolute_uri(url)
                # Only use values for fields that currently exist for the form.
                try:
                    row[field_indexes[field_entry.field_id]] = value
                except KeyError:
                    pass
            # Write out the row.
            csv.writerow(row)
        return response

    def file_view(self, request, field_entry_id):
        """
        Output the file for the requested field entry.
        """
        field = get_object_or_404(FieldEntry, id=field_entry_id)

        base_name = os.path.basename(field.value)
        mime_type = mimetypes.guess_type(base_name)[0]

        if not mime_type:
            raise Http404

        if not default_storage.exists(field.value):
            raise Http404

        data = default_storage.open(field.value).read()
        f = ContentFile(data)

        response = HttpResponse(f.read(), content_type=mime_type)
        response['Content-Disposition'] = 'filename=%s' % base_name
        return response


admin.site.register(Form, FormAdmin)
