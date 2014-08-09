import uuid

from datetime import timedelta, datetime
from django.db import models
from tendenci.apps.user_groups.models import Group
from tendenci.apps.user_groups.utils import get_default_group
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.auth.models import AnonymousUser

from tendenci.core.categories.models import CategoryItem
from tagging.fields import TagField
from tendenci.core.base.fields import SlugField
from tendenci.core.base.utils import now_localized
from tendenci.core.perms.models import TendenciBaseModel
from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.addons.jobs.managers import JobManager
from tinymce import models as tinymce_models
from tendenci.core.meta.models import Meta as MetaTags
from tendenci.addons.jobs.module_meta import JobMeta
from tendenci.apps.invoices.models import Invoice


class BaseJob(TendenciBaseModel):
    guid = models.CharField(max_length=40)
    title = models.CharField(max_length=250)
    slug = SlugField(_('URL Path'), unique=True)
    description = tinymce_models.HTMLField()
    list_type = models.CharField(max_length=50)  # premium or regular

    code = models.CharField(max_length=50, blank=True)  # internal job-code
    location = models.CharField(max_length=500, null=True, blank=True)  # cannot be foreign, needs to be open 'Texas' 'All 50 States' 'US and International'
    skills = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    education = models.TextField(blank=True)
    level = models.CharField(max_length=50, blank=True)  # e.g. entry, part-time, permanent, contract
    period = models.CharField(max_length=50, blank=True)  # full time, part time, contract
    is_agency = models.BooleanField()  # defines if the job posting is by a third party agency

    contact_method = models.TextField(blank=True)  # preferred method - email, phone, fax. leave open field for user to define
    position_reports_to = models.CharField(max_length=200, blank=True)  # manager, CEO, VP, etc
    salary_from = models.CharField(max_length=50, blank=True)
    salary_to = models.CharField(max_length=50, blank=True)
    computer_skills = models.TextField(blank=True)

    # date related fields
    requested_duration = models.IntegerField()  # 30, 60, 90 days - should be relational table
    pricing = models.ForeignKey('JobPricing', null=True)  # selected pricing based on requested_duration
    activation_dt = models.DateTimeField(null=True, blank=True)  # date job listing was activated
    post_dt = models.DateTimeField(null=True, blank=True)  # date job was posted (same as create date?)
    expiration_dt = models.DateTimeField(null=True, blank=True)  # date job expires based on activation date and duration
    start_dt = models.DateTimeField(null=True, blank=True)  # date job starts(defined by job poster)

    job_url = models.CharField(max_length=300, blank=True)  # link to other (fuller) job posting
    syndicate = models.BooleanField(_('Include in RSS feed'), blank=True, default=True)
    design_notes = models.TextField(blank=True)

    #TODO: foreign
    contact_company = models.CharField(max_length=300, blank=True)
    contact_name = models.CharField(max_length=150, blank=True)
    contact_address = models.CharField(max_length=50, blank=True)
    contact_address2 = models.CharField(max_length=50, blank=True)
    contact_city = models.CharField(max_length=50, blank=True)
    contact_state = models.CharField(max_length=50, blank=True)
    contact_zip_code = models.CharField(max_length=50, blank=True)
    contact_country = models.CharField(max_length=50, blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    contact_fax = models.CharField(max_length=50, blank=True)
    contact_email = models.CharField(max_length=300, blank=True)
    contact_website = models.CharField(max_length=300, blank=True)

    meta = models.OneToOneField(MetaTags, null=True)
    group = models.ForeignKey(Group, null=True, default=get_default_group, on_delete=models.SET_NULL)
    tags = TagField(blank=True)

    invoice = models.ForeignKey(Invoice, blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, default='')
    member_price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    member_count = models.IntegerField(blank=True, null=True)
    non_member_price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    non_member_count = models.IntegerField(blank=True, null=True)

    categories = generic.GenericRelation(
        CategoryItem,
        object_id_field="object_id",
        content_type_field="content_type"
    )
    perms = generic.GenericRelation(
        ObjectPermission,
        object_id_field="object_id",
        content_type_field="content_type"
    )

    objects = JobManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())

        super(BaseJob, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title

    # Called by payments_pop_by_invoice_user in Payment model.
    def get_payment_description(self, inv):
        """
        The description will be sent to payment gateway and displayed on invoice.
        If not supplied, the default description will be generated.
        """
        return 'Tendenci Invoice %d for Job: %s (%d).' % (
            inv.id,
            self.title,
            inv.object_id,
        )

    def make_acct_entries(self, user, inv, amount, **kwargs):
        """
        Make the accounting entries for the job sale
        """
        from tendenci.apps.accountings.models import Acct, AcctEntry, AcctTran
        from tendenci.apps.accountings.utils import make_acct_entries_initial, make_acct_entries_closing

        ae = AcctEntry.objects.create_acct_entry(user, 'invoice', inv.id)
        if not inv.is_tendered:
            make_acct_entries_initial(user, ae, amount)
        else:
            # payment has now been received
            make_acct_entries_closing(user, ae, amount)

            # #CREDIT job SALES
            acct_number = self.get_acct_number()
            acct = Acct.objects.get(account_number=acct_number)
            AcctTran.objects.create_acct_tran(user, ae, acct, amount * (-1))

    def get_acct_number(self, discount=False):
        if discount:
            return 462500
        else:
            return 402500

    def auto_update_paid_object(self, request, payment):
        """
        Update the object after online payment is received.
        """
        if not request.user.profile.is_superuser:
            self.status_detail = 'paid - pending approval'

        self.activation_dt = datetime.now()
        self.expiration_dt = self.activation_dt + timedelta(days=self.requested_duration)
        self.save()

    @property
    def opt_app_label(self):
        return self._meta.app_label

    @property
    def opt_module_name(self):
        return self._meta.module_name

    @property
    def category_set(self):
        items = {}
        for cat in self.categories.select_related('category__name', 'parent__name'):
            if cat.category:
                items["category"] = cat.category
            elif cat.parent:
                items["sub_category"] = cat.parent
        return items


class Job(BaseJob):

    class Meta:
        permissions = (("view_job", _("Can view job")),)
        verbose_name = _("Job")
        verbose_name_plural = _("Jobs")

    def get_meta(self, name):
        """
        This method is standard across all models that are
        related to the Meta model.  Used to generate dynamic
        meta information niche to this model.
        """
        return JobMeta().get_meta(self, name)

    @models.permalink
    def get_absolute_url(self):
        return ("job", [self.slug])

    @models.permalink
    def get_approve_url(self):
        return ("job.approve", [self.id])


class JobPricing(models.Model):
    title = models.CharField(max_length=40, blank=True, null=True)
    guid = models.CharField(max_length=40)
    duration = models.IntegerField(blank=True)
    regular_price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0)
    premium_price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0)
    regular_price_member = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0)
    premium_price_member = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0)
    show_member_pricing = models.BooleanField()
    include_tax = models.BooleanField(default=False)
    tax_rate = models.DecimalField(blank=True, max_digits=5, decimal_places=4, default=0,
                                   help_text=_('Example: 0.0825 for 8.25%.'))
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="job_pricing_creator",  null=True, on_delete=models.SET_NULL)
    creator_username = models.CharField(max_length=50, null=True)
    owner = models.ForeignKey(User, related_name="job_pricing_owner", null=True, on_delete=models.SET_NULL)
    owner_username = models.CharField(max_length=50, null=True)
    status = models.BooleanField(default=True)

    class Meta:
        permissions = (("view_jobpricing", _("Can view job pricing")),)
        verbose_name = _("Job Pricing")
        verbose_name_plural = _("Job Pricings")

    def __unicode__(self):
        price = "%s/%s" % (self.regular_price, self.premium_price)
        return "%s: %s Days for %s" % (self.get_title(), self.duration, price)

    def get_title(self):
        if self.title:
            return self.title
        return "Untitled"

    def save(self, user=None, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
            if user and user.id:
                self.creator = user
                self.creator_username = user.username
        if user and user.id:
            self.owner = user
            self.owner_username = user.username
        if not self.regular_price_member:
            self.regular_price_member = 0
        if not self.premium_price_member:
            self.premium_price_member = 0
        if not self.regular_price:
            self.regular_price = 0
        if not self.premium_price:
            self.premium_price = 0

        super(JobPricing, self).save(*args, **kwargs)

    def get_price_for_user(self, user=AnonymousUser(), list_type='regular'):
        if not user.is_anonymous() and user.profile.is_member:
            if list_type == 'regular':
                return self.regular_price_member
            else:
                return self.premium_price_member
        else:
            if list_type == 'regular':
                return self.regular_price
            else:
                return self.premium_price
