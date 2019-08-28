from builtins import str
from csv import writer
from datetime import datetime

from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.urls import reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.theme.templatetags.static import static
from tendenci.apps.forms_builder.forms.models import Form, Field, FieldEntry, Pricing, FormEntry
from tendenci.apps.forms_builder.forms.forms import FormAdminForm, FormForField, PricingForm
from tendenci.apps.forms_builder.forms.utils import form_entries_to_csv_writer

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
        "admin_link_export", 'export_all_link', "admin_link_view", 'group',)
    list_display_links = ("title",)
#    list_filter = ("status",)
    search_fields = ("title", "intro", "response", "email_from",
        "email_copies")
#    radio_fields = {"status": admin.HORIZONTAL}
    prepopulated_fields = {'slug': ['title']}
    list_filter = ('group', )

    if not get_setting('module', 'recurring_payments', 'enabled'):
        payment_fields = ("custom_payment", "payment_methods")
    else:
        payment_fields = ("custom_payment", 'recurring_payment', "payment_methods")

    position_fields = ("intro_position", "fields_position", "pricing_position")
    section_name_fields = ("intro_name", "fields_name", "pricing_name")

    fieldsets = (
        (None, {"fields": ("title", "slug", "intro", "response", "completion_url", 'group', "template")}),
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
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js',
            static('js/global/tinymce.event_handlers.js'),
            static('js/admin/form-fields-inline-ordering.js'),
            static('js/admin/form-field-dynamic-hiding.js'),
            static('js/admin/form-position.js'),
            static('js/admin/tax_fields.js'),
        )
        css = {'all': [static('css/admin/dynamic-inlines-with-sort.css')], }

    @mark_safe
    def export_all_link(self, obj):
        link = '-----'
        if obj.has_files():
            link = '<a href="%s" title="Export all">Export entries (including uploaded files)</a>' % reverse('form_entries_export_full', args=[obj.pk])
        return link
    export_all_link.short_description = ''

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, unquote(object_id))
        if obj:
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
        extra_urls = [
            url(r'^export/(?P<form_id>\d+)/$',
                self.admin_site.admin_view(self.export_view),
                name="forms_form_export"),
            url(r'^file/(?P<field_entry_id>\d+)/$',
                self.admin_site.admin_view(self.file_view),
                name="forms_form_file"),
        ]
        return extra_urls + urls

    def export_view(self, request, form_id):
        """
        Output a CSV file to the browser containing the entries for the form.
        """
        form = get_object_or_404(Form, id=form_id)
        response = HttpResponse(content_type='text/csv')
        csvname = '%s-%s.csv' % (form.slug, slugify(datetime.now().ctime()))
        response['Content-Disposition'] = 'attachment; filename="%s"' % csvname
        csv_writer = writer(response)
        # Write out the column names and store the index of each field
        # against its ID for building each entry row. Also store the IDs of
        # fields with a type of FileField for converting their field values
        
        form_entries_to_csv_writer(csv_writer, form)
        
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
        response['Content-Disposition'] = 'filename="%s"' % base_name
        return response


class FormEntryAdmin(admin.ModelAdmin):
    model = FormEntry
    list_display = ['entry_time', 'form', 'first_name', 'last_name', 'email']
    list_filter = ['form']
    ordering = ("-entry_time",)

    def first_name(self, instance):
        return instance.get_first_name()
    
    def last_name(self, instance):
        return instance.get_last_name()
    
    def email(self, instance):
        return instance.get_email_address()

    def has_add_permission(self, request):
        return False
    
    def change_view(self, request, object_id, form_url='',
                    extra_context=None):
        return HttpResponseRedirect(
                    reverse('form_entry_detail', args=[object_id])
                )


admin.site.register(Form, FormAdmin)
admin.site.register(FormEntry, FormEntryAdmin)
