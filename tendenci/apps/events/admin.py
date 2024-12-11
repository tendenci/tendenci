from csv import writer
from datetime import datetime
import time as ttime

from django import forms
from django.contrib import admin, messages
from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.urls import path, re_path
from django.http import HttpResponse, Http404, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils.encoding import iri_to_uri
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.events.models import (CustomRegForm, CustomRegField, Type, StandardRegForm,
                                         CustomRegFormEntry, CustomRegFieldEntry, Event,
                                         CEUCategory, SignatureImage, CertificateImage,
                                         RegistrantCredits, VirtualEventCreditsLogicConfiguration,
                                         ZoomAPIConfiguration,
                                         AssetsPurchase, Place)
from tendenci.apps.events.forms import (CustomRegFormAdminForm, CustomRegFormForField, TypeForm,
                                        StandardRegAdminForm)
from tendenci.apps.events.utils import iter_registrant_credits
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.site_settings.utils import delete_settings_cache, get_setting
from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.theme.templatetags.static import static
from tendenci.apps.base.utils import tcurrency


class EventAdmin(TendenciBaseModelAdmin):

    list_display = (
        'title',
        'enable_private_slug',
        'start_dt',
        'status_detail',
    )
    search_fields = ("title",)
    list_filter = ('enable_private_slug', 'place')
    ordering = ['-start_dt']

    def has_add_permission(self, request):
        return False

    def change_view(self, request, object_id, form_url='',
                    extra_context=None):
        return HttpResponseRedirect(
                    reverse('event.edit', args=[object_id])
                )


class EventPlaceAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'description',
        'address',
        'city',
        'state',
        'is_zoom_webinar',
        'event_counts'
    )
    list_display_links = ('id',)
    search_fields = ("name",)
    list_filter = ('name', 'address',)
    ordering = ['name','address', 'city']
    actions = ['merge']

    def merge(self, request, queryset):
        main = queryset[0]
        tail = queryset[1:]
        for place_to_merge in tail:
            Event.objects.filter(place=place_to_merge).update(place=main)
            place_to_merge.delete()

    merge.short_description = "Merge places"

    @mark_safe
    def event_counts(self, obj):
        if obj:
            counts = obj.event_set.all().count()
            if counts > 0:
                events_url = reverse('admin:events_event_changelist')
                return f'<a href="{events_url}?place__id__exact={obj.id}">{counts}</a>'
        return '0'
    event_counts.short_description = _('Events')

    def has_add_permission(self, request):
        return False

admin.site.register(Place, EventPlaceAdmin)


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


class CEUSubCategoryFormSet(BaseInlineFormSet):

    def clean(self):
        super(CEUSubCategoryFormSet, self).clean()

        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue

            data = form.cleaned_data

            if (data.get('DELETE') and form.instance.eventcredit_set.available().exists()):
                raise ValidationError(_(f'You cannot delete this sub-category "{form.instance}" - It is being used by events.'))


class CEUCategoryAdminInline(admin.TabularInline):
    fieldsets = ((None, {'fields': ('code', 'name',)}),)
    model = CEUCategory
    extra = 0
    verbose_name = _("Continuing Education Unit Sub-Category")
    verbose_name_plural = _("Continuing Education Unit Sub-Categories")
    formset = CEUSubCategoryFormSet


class CEUCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name',)
    list_display_links = ('name',)
    fieldsets = ((None, {'fields': ('code', 'name',)}),)
    inlines = (CEUCategoryAdminInline,)
    verbose_name = _("Continuing Education Unit Category")
    verbose_name_plural = _("Continuing Education Unit Categories")

    def get_queryset(self, request):
        qs = super(CEUCategoryAdmin, self).get_queryset(request)
        return qs.filter(parent__isnull=True)


class SignatureImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)


class CertificateImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)


class RegistrantCreditsEventFilter(admin.SimpleListFilter):
    """Filter Events that have credits assigned to registrants"""
    title = _('Event')
    parameter_name = 'event'

    def lookups(self, request, model_admin):
        events = []
        events_pk = RegistrantCredits.objects.all().values_list('event', flat=True)

        for event in Event.objects.filter(pk__in=events_pk).order_by('-start_dt'):
            events.append((str(event.id), str(event)))
        return events

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(event__id__exact=self.value())
        else:
            return queryset


class CreditNameFilter(admin.SimpleListFilter):
    """Filter by credit name"""
    title = _('Credit Name')
    parameter_name = 'ceu_subcategory'

    def lookups(self, request, model_admin):
        ceu_categories = CEUCategory.objects.filter(parent__isnull=False
                                    ).order_by('parent', 'name')
        ceu_cats_list = []
        for ceu_cat in ceu_categories:
            ceu_cats_list.append((str(ceu_cat.id), f'{ceu_cat.parent.name} - {ceu_cat.name}'))
                                    
        return ceu_cats_list

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(event_credit__ceu_subcategory=self.value())
        else:
            return queryset


class RegistrantCreditsAdmin(admin.ModelAdmin):
    list_display = ('id', 'registrant', 'event_code', 'event_link', 'credit_name', 'credits', 'alternate_ceu_id',)
    if get_setting('module', 'events', 'showmembernumber2'):
        list_display += ('show_member_number_2',)
    list_display += ('released',)
    list_editable = ('credits', 'released')
    search_fields = ('event__title', 'event__event_code',)
    readonly_fields = ('registrant', 'event_credit', 'event_link')
    list_filter = ('released', CreditNameFilter, RegistrantCreditsEventFilter)
    actions = ["release", 'unrelease', "export_selected"]


    def event_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            obj.event.get_absolute_url(),
            obj.event
        ))
    event_link.short_description = 'event'

    def release(self, request, queryset):
        """Release all credits"""
        queryset.update(released=True)
    release.short_description=_("Release selected credits")
    
    def unrelease(self, request, queryset):
        """Un-Release all selected credits"""
        queryset.update(released=False)
    unrelease.short_description=_("Unrelease selected credits")

    def show_member_number_2(self, obj):
        user = obj.registrant.user
        if user and hasattr(user, 'profile'):
            return user.profile.member_number_2
        return ""
    show_member_number_2.short_description = get_setting('module', 'users', 'membernumber2label')

    def export_selected(self, request, queryset):
        """
        Exports the selected credits.
        """
        response = StreamingHttpResponse(
        streaming_content=(iter_registrant_credits(queryset)),
        content_type='text/csv',)
        response['Content-Disposition'] = f'attachment;filename=registrant_credits_export_{ttime.time()}.csv'
        return response

    export_selected.short_description = 'Export selected credits'

    def has_delete_permission(self, request, obj=None):
        """Don't allow deleting released credits"""
        result = super().has_delete_permission(request, obj=obj)

        if obj and obj.released:
            self.message_user(
                request,
                _(f"Credits for {obj.registrant} in {obj.credit_name} have already been released.")
            )
            return False
        return result

    def has_add_permission(self, request):
        return False

    def event_code(self, obj):
        return obj.event.event_code
    event_code.short_description = _('Event Code')


class VirtualEventCreditsLogicConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        'edit',
        'credit_period',
        'credit_period_questions',
        'full_credit_percent',
        'full_credit_questions',
        'half_credits_allowed',
        'half_credit_periods',
        'half_credit_credits',
    )

    def edit(self, obj):
        return 'Edit'

    def has_add_permission(self, request):
        return not VirtualEventCreditsLogicConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class ZoomAPIConfigurationForm(forms.ModelForm):
    class Meta:
        model = ZoomAPIConfiguration
        fields = '__all__'
        widgets = {
            'sdk_client_secret': forms.PasswordInput(
                render_value = True, attrs={'autocomplete': 'new-password'}),
            'oauth_client_secret': forms.PasswordInput(
                render_value = True, attrs={'autocomplete': 'new-password'})
        }


class ZoomAPIConfigurationAdmin(admin.ModelAdmin):
    """Configure Zoom API credentials"""
    form = ZoomAPIConfigurationForm
    list_display=('account_name', 'use_as_default')
    list_editable=('use_as_default',)

    def save_model(self, request, obj, form, change):
        if obj.use_as_default:
            ZoomAPIConfiguration.objects.update(use_as_default=False)
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if obj and not obj.use_as_default and ZoomAPIConfiguration.objects.filter(
                use_as_default=True).exists():
            return ['use_as_default']
        return super().get_readonly_fields(request, obj)


if get_setting('module', 'events', 'enable_zoom'):
    admin.site.register(ZoomAPIConfiguration, ZoomAPIConfigurationAdmin)

if get_setting('module', 'events', 'use_credits'):
    admin.site.register(CEUCategory, CEUCategoryAdmin)

    if get_setting('module', 'events', 'enable_zoom'):
        admin.site.register(VirtualEventCreditsLogicConfiguration, VirtualEventCreditsLogicConfigurationAdmin)

class AssetsPurchaseAdmin(admin.ModelAdmin):

    list_display = ('id',
        'first_name',
        'last_name',
        'email',
        'user_profile',
        'amount',
        'event',
        'pricing',
        'get_invoice',
        'create_dt',
        'status_detail'
    )
    fieldsets = (
        (None, {'fields': ('event', 'user', 'first_name', 'last_name', 'email',
                           'amount', 'pricing',
                           'payment_method',
                            'invoice',
                           'status_detail',)},),
    )
    search_fields = ("first_name", 'last_name',
                     'email', 'event__title')
    list_filter = (('event', admin.RelatedOnlyFieldListFilter),)
    ordering = ['-create_dt']
    readonly_fields = ('user', 'event', 'invoice',)

    @mark_safe
    def get_invoice(self, instance):
        if instance.invoice:
            if instance.invoice.balance > 0:
                return f'<a href="{instance.invoice.get_absolute_url()}" title="Invoice">#{instance.invoice.id} ({tcurrency(instance.invoice.balance)})</a>'
            else:
                return f'<a href="{instance.invoice.get_absolute_url()}" title="Invoice">#{instance.invoice.id}</a>'
        return ""
    get_invoice.short_description = 'Invoice'

    @mark_safe
    def user_profile(self, instance):
        url = reverse('profile', args=[instance.user.username])
        return f'<a href="{url}">{instance.user.username}</a>'
    user_profile.short_description = _('User')

    def has_add_permission(self, request):
        return False

admin.site.register(AssetsPurchase, AssetsPurchaseAdmin)

admin.site.register(RegistrantCredits, RegistrantCreditsAdmin)
admin.site.register(SignatureImage, SignatureImageAdmin)
admin.site.register(CertificateImage, CertificateImageAdmin)
admin.site.register(StandardRegForm, StandardRegFormAdmin)
admin.site.register(Event, EventAdmin)
