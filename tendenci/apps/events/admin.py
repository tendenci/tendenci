from csv import writer
from datetime import datetime

from django.contrib import admin, messages
from django.urls import reverse
from django.urls import path, re_path
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.utils.encoding import iri_to_uri
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.events.models import (CustomRegForm, CustomRegField, Type, StandardRegForm,
    CustomRegFormEntry, CustomRegFieldEntry, Event)
from tendenci.apps.events.forms import CustomRegFormAdminForm, CustomRegFormForField, TypeForm, StandardRegAdminForm
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.site_settings.utils import delete_settings_cache
from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.theme.templatetags.static import static


class EventAdmin(TendenciBaseModelAdmin):

    list_display = (
        'title',
        'enable_private_slug',
        'start_dt',
        'status_detail',
    )
    search_fields = ("title",)
    list_filter = ('enable_private_slug',)
    ordering = ['-start_dt']

    def has_add_permission(self, request):
        return False
    
    def change_view(self, request, object_id, form_url='',
                    extra_context=None):
        return HttpResponseRedirect(
                    reverse('event.edit', args=[object_id])
                )


class EventTypeAdmin(admin.ModelAdmin):
    form = TypeForm
    list_display = (
        'id',
        'name',
        'bg_color',
        'event_count',
        'reassign',
    )
    list_display_links = ('name',)

    @mark_safe
    def reassign(self, obj):

        return """<a href="%s">Reassign all events from this type</a>
            """ % (reverse('event.reassign_type', args=[obj.id]))
    reassign.short_description = _('Reassign Link')

    class Media:
        css = {'all': [static('css/admin/event-types-color-set.css')], }

admin.site.register(Type, EventTypeAdmin)


class CustomRegFieldAdminForm(CustomRegFormForField):
    class Meta:
        model = CustomRegField
        # django 1.8 requires fields or exclude
        exclude = ()


class CustomRegFieldAdmin(admin.TabularInline):
    model = CustomRegField
    form = CustomRegFieldAdminForm
    extra = 0
    verbose_name = 'custom field'
    ordering = ("position",)
    template = "events/admin/tabular.html"


def clone_forms(modeladmin, request, queryset):
    for form in queryset:
        cloned = form.clone()
        if not cloned.name.startswith('Clone of'):
            cloned.name = 'Clone of %s' % cloned.name
        cloned.name = cloned.name[:50]
        cloned.save()

clone_forms.short_description = 'Clone selected forms'


class CustomRegFormAdmin(admin.ModelAdmin):
    inlines = (CustomRegFieldAdmin,)
    list_display = ('id', "name", "preview_link", "for_event", "notes", "status",)
    list_display_links = ("name",)
    search_fields = ("name", "notes", "status",)
    fieldsets = (
        (None, {"fields": ("name", "notes", 'status')}),
        (_('Add fields to your form'), {'fields': (('first_name', 'last_name', 'email'),
                                                 ('company_name', 'phone', 'position_title'),
                                                 ('address', 'city', 'state'),
                                                 ('zip', 'country', 'meal_option'),
                                                 ('comments',)),
                                     'classes': ('mapped-fields',),
                                     'description': _('The fields you selected will be automatically added to ' +
                                     'your form. These fields are mapped to the user fields in ' +
                                     'the registration. To delete a mapped field, uncheck its corresponding ' +
                                     'check box here. Please do not add another custom field ' +
                                     'if you can find a field here. To add a custom field, click Add a ' +
                                     'Custom Field in the Fields section below.')})
    )

    form = CustomRegFormAdminForm
    actions = [clone_forms]

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js',
            static('js/global/tinymce.event_handlers.js'),
            static('js/admin/form-fields-inline-ordering.js'),
            static('js/admin/form-field-dynamic-hiding.js'),
        )
        css = {'all': [static('css/admin/dynamic-inlines-with-sort.css')], }

    @mark_safe
    def preview_link(self, obj):
        return """<a href="%s">preview</a>
            """ % (reverse('event.custom_reg_form_preview', args=[obj.id]))
    preview_link.short_description = _('Preview Link')

    @mark_safe
    def for_event(self, obj):
        [regconf] = obj.regconfs.all()[:1] or [None]
        if regconf:
            event = regconf.event
            return """<a href="%s">%s(ID:%d)</a>
            """ % (reverse('event', args=[event.id]), event.title, event.id)
        return ''
    for_event.short_description = _('For Event')

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = get_object_or_404(CustomRegForm, id=object_id)
        has_regconf = obj.has_regconf
        extra_context = extra_context or {}
        extra_context.update({'has_regconf': has_regconf})
        result = super(CustomRegFormAdmin, self).change_view(request,
                        object_id, form_url=form_url, extra_context=extra_context)

        if '_addanother' not in request.POST and '_continue' not in request.POST and 'next' in request.GET:
            result['Location'] = iri_to_uri("%s") % request.GET.get('next')
        return result

    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)

        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username

        instance.owner = request.user
        instance.owner_username = request.user.username

        # save the object
        instance.save()

        form.save_m2m()

        return instance

    def log_deletion(self, request, object, object_repr):
        super(CustomRegFormAdmin, self).log_deletion(request, object, object_repr)
        EventLog.objects.log(instance=object)

    def log_change(self, request, object, message):
        super(CustomRegFormAdmin, self).log_change(request, object, message)
        EventLog.objects.log(**{
            'event_id': 176200,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name,
                                                    object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        })

    def log_addition(self, request, object, message):
        super(CustomRegFormAdmin, self).log_addition(request, object, message)
        log_defaults = {
            'event_id': 176100,
            'event_data': '%s (%d) added by %s' % (object._meta.object_name,
                                                   object.pk, request.user),
            'description': '%s added' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)

    def export_view(self, request, regform_id):
        """
        Output a CSV file to the browser containing the entries for the form.
        """
        form = get_object_or_404(CustomRegForm, id=regform_id)
        if not form.has_regconf:
            raise Http404
        response = HttpResponse(content_type='text/csv')
        csvname = '%s-%s.csv' % (form.for_event, slugify(datetime.now().ctime()))
        response['Content-Disposition'] = 'attachment; filename="%s"' % csvname
        csv = writer(response)
        # Write out the column names and store the index of each field
        # against its ID for building each entry row. Also store the IDs of
        # fields with a type of FileField for converting their field values
        # into download URLs.
        columns = []
        field_indexes = {}
        for field in form.fields.all().order_by('position', 'id'):
            columns.append(field.label)
            field_indexes[field.id] = len(field_indexes)

        csv.writerow(columns)
        # # Loop through each field value order by entry, building up each
        # # entry as a row.
        entries = CustomRegFormEntry.objects.filter(form=form).order_by('pk')
        for entry in entries:
            values = CustomRegFieldEntry.objects.filter(entry=entry)
            row = [""] * len(columns)

            for field_entry in values:
                value = field_entry.value
                # Only use values for fields that currently exist for the form.
                try:
                    row[field_indexes[field_entry.field_id]] = value
                except KeyError:
                    pass
            # Write out the row.
            csv.writerow(row)
        return response

    def get_urls(self):
        """
        Add the export view to urls.
        """
        urls = super(CustomRegFormAdmin, self).get_urls()
        extra_urls = [
            re_path(r'^export/(?P<regform_id>\d+)/$',
                self.admin_site.admin_view(self.export_view),
                name="customregform_export"),
        ]
        return extra_urls + urls

admin.site.register(CustomRegForm, CustomRegFormAdmin)


class StandardRegFormAdmin(admin.ModelAdmin):

    def get_urls(self):
        """
        Add the export view to urls.
        """
        urls = super(StandardRegFormAdmin, self).get_urls()
        extra_urls = [
            re_path(r'^edit',
                self.admin_site.admin_view(self.edit_regform_view),
                name="standardregform_edit"),
        ]
        return extra_urls + urls

    def edit_regform_view(self, request):
        form = StandardRegAdminForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            form.apply_changes()
            delete_settings_cache('module', 'events')
            messages.success(request, "Successfully updated Standard Registration Form")
            return redirect(reverse('admin:standardregform_edit'))

        return render_to_resp(request=request,
            template_name='admin/events/standardregform/standard_reg_form_edit.html',
            context={'adminform': form})

    def changelist_view(self, request, extra_context=None):
        return redirect(reverse('admin:standardregform_edit'))

    def has_add_permission(self, request):
        return False


admin.site.register(StandardRegForm, StandardRegFormAdmin)
admin.site.register(Event, EventAdmin)
