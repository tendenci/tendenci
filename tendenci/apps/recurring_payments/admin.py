from django.contrib import admin
from django.core.urlresolvers import reverse

from django.contrib.admin import widgets
from django.db import models
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.recurring_payments.models import RecurringPayment, PaymentProfile
from tendenci.apps.recurring_payments.forms import RecurringPaymentForm

from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.base.utils import tcurrency

class NoAddAnotherModelAdmin(admin.ModelAdmin):
    """Remove the add-another + sign
    """
    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Hook for specifying the form Field instance for a given database Field
        instance.

        If kwargs are given, they're passed to the form Field's constructor.
        """
        request = kwargs.pop("request", None)

        # If the field specifies choices, we don't need to look for special
        # admin widgets - we just need to use a select widget of some kind.
        if db_field.choices:
            return self.formfield_for_choice_field(db_field, request, **kwargs)

        # ForeignKey or ManyToManyFields
        if isinstance(db_field, (models.ForeignKey, models.ManyToManyField)):
            # Combine the field kwargs with any options for formfield_overrides.
            # Make sure the passed in **kwargs override anything in
            # formfield_overrides because **kwargs is more specific, and should
            # always win.
            if db_field.__class__ in self.formfield_overrides:
                kwargs = dict(self.formfield_overrides[db_field.__class__], **kwargs)

            # Get the correct formfield.
            if isinstance(db_field, models.ForeignKey):
                formfield = self.formfield_for_foreignkey(db_field, request, **kwargs)
            elif isinstance(db_field, models.ManyToManyField):
                formfield = self.formfield_for_manytomany(db_field, request, **kwargs)

            # For non-raw_id fields, wrap the widget with a wrapper that adds
            # extra HTML -- the "add other" interface -- to the end of the
            # rendered output. formfield can be None if it came from a
            # OneToOneField with parent_link=True or a M2M intermediary.
#            if formfield and db_field.name not in self.raw_id_fields:
#                related_modeladmin = self.admin_site._registry.get(
#                                                            db_field.rel.to)
#                can_add_related = bool(related_modeladmin and
#                            related_modeladmin.has_add_permission(request))
#                formfield.widget = widgets.RelatedFieldWidgetWrapper(
#                            formfield.widget, db_field.rel, self.admin_site,
#                                    can_add_related=can_add_related)
#
#            return formfield

        # If we've got overrides for the formfield defined, use 'em. **kwargs
        # passed to formfield_for_dbfield override the defaults.
        for klass in db_field.__class__.mro():
            if klass in self.formfield_overrides:
                kwargs = dict(self.formfield_overrides[klass], **kwargs)
                return db_field.formfield(**kwargs)

        # For any other type of field, just call its formfield() method.
        return db_field.formfield(**kwargs)


class RecurringPaymentAdmin(NoAddAnotherModelAdmin):
    def edit_payment_info_link(self):
        # customer_profile_id
        if not self.customer_profile_id:
            pp = None
        else:
            pp = PaymentProfile.objects.filter(
                                    customer_profile_id=self.customer_profile_id,
                                    status=True, status_detail='active')
        link = reverse('recurring_payment.authnet.update_payment_info', args=[self.id])
        if pp:
            pp = pp[0]
            return '<a href="%s">Edit payment info</a><br />Last updated by %s<br /> on %s' % (
                                                                        link,
                                                                        pp.owner,
                                                                        pp.update_dt.strftime('%Y-%m-%d'))
        else:
            return '<a href="%s">Add payment info</a>' % (link)
    edit_payment_info_link.allow_tags = True

    def view_on_site(self, obj):
        link = reverse('recurring_payment.view_account', args=[obj.id])
        return '<a href="%s">View on site</a>' % (link)
    view_on_site.allow_tags = True

    def how_much_to_pay(self):
        if self.billing_frequency == 1:
            return '%s/%s' % (tcurrency(self.payment_amount), self.billing_period)
        else:
            return '%s/%d %ss' % (tcurrency(self.payment_amount), self.billing_frequency, self.billing_period)

    list_display = ['user', edit_payment_info_link, view_on_site,
                    'description', 'billing_start_dt',
                     how_much_to_pay,
                     'status_detail']
    list_filter = ['status_detail']

    fieldsets = (
        (None, {'fields': ('user', 'url', 'description',)}),
        (_("Billing Settings"), {'fields': ('payment_amount', ('taxable', 'tax_rate',),
                           'billing_start_dt', 'billing_cycle', 'billing_dt_select', )}),
        (_("Trial Period"), {'fields': ('has_trial_period',  'trial_amount',
                           'trial_period_start_dt',  'trial_period_end_dt',  ),
                          'description': '*** Note that if the trial period overlaps with ' + \
                          'the initial billing cycle start date, the trial period will end' + \
                          ' on the initial billing cycle start date.'}),
        (_('Other Options'), {'fields': ('status', 'status_detail',)}),
    )

    form = RecurringPaymentForm


    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)

        # billing_cycle
        billing_cycle = form.cleaned_data['billing_cycle']
        billing_cycle_list = billing_cycle.split(",")
        instance.billing_frequency = billing_cycle_list[0]
        instance.billing_period = billing_cycle_list[1]

        # billing_date
        billing_dt_select = form.cleaned_data['billing_dt_select']
        billing_dt_select_list = billing_dt_select.split(",")
        instance.num_days = billing_dt_select_list[0]
        instance.due_sore = billing_dt_select_list[1]

        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username

        # save the object
        instance.save()


        return instance

    def log_change(self, request, object, message):
        super(RecurringPaymentAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 1120200,
            'event_data': '%s for %s(%d) edited by %s' % (object._meta.object_name,
                                                    object.user, object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)

    def log_addition(self, request, object):
        super(RecurringPaymentAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 1120100,
            'event_data': '%s for %s(%d) added by %s' % (object._meta.object_name,
                                                   object.user, object.pk, request.user),
            'description': '%s added' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)

    def log_deletion(self, request, object, message):
        super(RecurringPaymentAdmin, self).log_deletion(request, object, message)
        log_defaults = {
            'event_id' : 1120300,
            'event_data': '%s for %s(%d) deleted by %s' % (object._meta.object_name,
                                                    object.user, object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)

admin.site.register(RecurringPayment, RecurringPaymentAdmin)
