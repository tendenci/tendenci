import uuid
from datetime import datetime, timedelta
from functools import reduce
import operator

from django.db.models import Q
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.auth.models import AnonymousUser
from django.template.defaultfilters import slugify

from tagging.fields import TagField
from timezone_field import TimeZoneField

from tendenci.libs.tinymce import models as tinymce_models
from tendenci.apps.meta.models import Meta as MetaTags
from tendenci.apps.base.fields import SlugField
from tendenci.apps.base.utils import correct_filename, get_timezone_choices
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.categories.models import CategoryItem
from tendenci.apps.invoices.models import Invoice
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.files.models import File
from tendenci.apps.directories.module_meta import DirectoryMeta
from tendenci.apps.directories.managers import DirectoryManager
from tendenci.apps.directories.choices import ADMIN_DURATION_CHOICES
from tendenci.libs.boto_s3.utils import set_s3_file_permission
from tendenci.apps.regions.models import Region
from tendenci.apps.entities.models import Entity
from tendenci.libs.abstracts.models import OrderingBaseModel
from tendenci.apps.base.utils import validate_email
from tendenci.apps.base.validators import UnicodeNameValidator


def file_directory(instance, filename):
    filename = correct_filename(filename)
    return 'directories/%d/%s' % (instance.id, filename)

class Category(OrderingBaseModel):
    name = models.CharField(max_length=255, validators=[UnicodeNameValidator()],)
    slug = models.SlugField()
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('slug', 'parent',)
        verbose_name_plural = _("Categories")
        ordering = ('position', 'name')
        app_label = 'directories'

    def __str__(self):
        return self.name

class Directory(TendenciBaseModel):

    guid = models.CharField(max_length=40)
    slug = SlugField(_('URL Path'), unique=True)
    entity = models.OneToOneField(Entity, blank=True, null=True,
                                  on_delete=models.SET_NULL,)
    timezone = TimeZoneField(verbose_name=_('Time Zone'), default='US/Central', choices=get_timezone_choices(), max_length=100)
    headline = models.CharField(_('Name'), max_length=200, blank=True)
    summary = models.TextField(blank=True)
    body = tinymce_models.HTMLField(_('Description'))
    source = models.CharField(max_length=300, blank=True)
    # logo = models.FileField(max_length=260, upload_to=file_directory,
    #                         help_text=_('Company logo. Only jpg, gif, or png images.'),
    #                         blank=True)

    logo_file = models.ForeignKey(File, null=True, on_delete=models.CASCADE)

    first_name = models.CharField(_('First Name'), max_length=100, blank=True)
    last_name = models.CharField(_('Last Name'), max_length=100, blank=True)
    address = models.CharField(_('Address'), max_length=100, blank=True)
    address2 = models.CharField(_('Address 2'), max_length=100, blank=True)
    city = models.CharField(_('City'), max_length=50, blank=True)
    state = models.CharField(_('State'), max_length=50, blank=True)
    zip_code = models.CharField(_('Zip Code'), max_length=50, blank=True)
    country = models.CharField(_('Country'), max_length=50, blank=True)
    region = models.ForeignKey(Region, blank=True, null=True, on_delete=models.SET_NULL)
    phone = models.CharField(max_length=50, blank=True)
    phone2 = models.CharField(_('Phone 2'), max_length=50, blank=True)
    fax = models.CharField(_('Fax'), max_length=50, blank=True)
    email = models.CharField(_('Email'), max_length=120, blank=True)
    email2 = models.CharField(_('Email 2'), max_length=120, blank=True)
    website = models.CharField(max_length=300, blank=True)

    renewal_notice_sent = models.BooleanField(default=False)
    list_type = models.CharField(_('List Type'), max_length=50, blank=True)
    requested_duration = models.IntegerField(_('Requested Duration'), default=0)
    pricing = models.ForeignKey('DirectoryPricing', null=True, on_delete=models.CASCADE)
    activation_dt = models.DateTimeField(_('Activation Date/Time'), null=True, blank=True)
    expiration_dt = models.DateTimeField(_('Expiration Date/Time'), null=True, blank=True)
    invoice = models.ForeignKey(Invoice, blank=True, null=True, on_delete=models.CASCADE)
    payment_method = models.CharField(_('Payment Method'), max_length=50, blank=True)
    
    # social media links
    linkedin = models.URLField(_('LinkedIn'), blank=True, default='')
    facebook = models.URLField(_('Facebook'), blank=True, default='')
    twitter = models.URLField(_('Twitter'), blank=True, default='')
    instagram = models.URLField(_('Instagram'), blank=True, default='')
    youtube = models.URLField(_('YouTube'), blank=True, default='')

    syndicate = models.BooleanField(_('Include in RSS feed'), default=True)
    design_notes = models.TextField(_('Design Notes'), blank=True)
    admin_notes = models.TextField(_('Admin Notes'), blank=True)
    tags = TagField(blank=True)

    # for podcast feeds
    enclosure_url = models.CharField(_('Enclosure URL'), max_length=500, blank=True)
    enclosure_type = models.CharField(_('Enclosure Type'), max_length=120, blank=True)
    enclosure_length = models.IntegerField(_('Enclosure Length'), default=0)

    # html-meta tags
    meta = models.OneToOneField(MetaTags, null=True, on_delete=models.SET_NULL)

    cat = models.ForeignKey(Category, verbose_name=_("Category"),
                                 related_name="directory_cat", null=True, on_delete=models.SET_NULL)
    sub_cat = models.ForeignKey(Category, verbose_name=_("Sub Category"),
                                 related_name="directory_subcat", null=True, on_delete=models.SET_NULL)
    cats = models.ManyToManyField(Category, verbose_name=_("Categories"),
                                  related_name="directory_cats",)
    sub_cats = models.ManyToManyField(Category, verbose_name=_("Sub Categories"),
                                  related_name="directory_subcats",)
    # legacy categories needed for data migration
    categories = GenericRelation(CategoryItem,
                                          object_id_field="object_id",
                                          content_type_field="content_type")
    perms = GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")
    
    affiliates = models.ManyToManyField("Directory", through='Affiliateship')

    objects = DirectoryManager()

    class Meta:
#         permissions = (("view_directory",_("Can view directory")),)
        verbose_name = _("Directory")
        verbose_name_plural = _("Directories")
        app_label = 'directories'

    def get_meta(self, name):
        """
        This method is standard across all models that are
        related to the Meta model.  Used to generate dynamic
        methods coupled to this instance.
        """
        return DirectoryMeta().get_meta(self, name)

    def __str__(self):
        return self.headline

    def get_absolute_url(self):
        return reverse('directory', args=[self.slug])

    def get_renew_url(self):
        return reverse('directory.renew', args=[self.id])

    def set_slug(self):
        if not self.slug:
            slug = slugify(self.headline)
            count = str(Directory.objects.count())
            if len(slug) + len(count) >= 99:
                self.slug = '%s-%s' % (slug[:99-len(count)], count)
            else:
                self.slug = '%s-%s' % (slug, count)

    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid4())

        super(Directory, self).save(*args, **kwargs)
        if self.logo:
            if self.is_public():
                set_s3_file_permission(self.logo.name, public=True)
            else:
                set_s3_file_permission(self.logo.name, public=False)

    def is_public(self):
        return all([self.allow_anonymous_view,
                self.status,
                self.status_detail in ['active']])

    def has_social_media(self):
        return any([self.linkedin, self.facebook, self.twitter, self.instagram, self.youtube])

    @property
    def logo(self):
        """
        This represents the logo FileField

        Originally this was a FileField, but later
        we added the attribute logo_file to leverage
        the File model.  We then replaced the logo
        property with this convience method for
        backwards compatibility.
        """
        if self.logo_file:
            return self.logo_file.file

    def get_logo_url(self):
        if not self.logo_file:
            return u''

        return reverse('file', args=[self.logo_file.pk])

    # Called by payments_pop_by_invoice_user in Payment model.
    def get_payment_description(self, inv):
        """
        The description will be sent to payment gateway and displayed on invoice.
        If not supplied, the default description will be generated.
        """
        return 'Tendenci Invoice %d for Directory: %s (%d).' % (
            inv.id,
            self.headline,
            inv.object_id,
        )

    def make_acct_entries(self, user, inv, amount, **kwargs):
        """
        Make the accounting entries for the directory sale
        """
        from tendenci.apps.accountings.models import Acct, AcctEntry, AcctTran
        from tendenci.apps.accountings.utils import make_acct_entries_initial, make_acct_entries_closing

        ae = AcctEntry.objects.create_acct_entry(user, 'invoice', inv.id)
        if not inv.is_tendered:
            make_acct_entries_initial(user, ae, amount)
        else:
            # payment has now been received
            make_acct_entries_closing(user, ae, amount)

            # #CREDIT directory SALES
            acct_number = self.get_acct_number()
            acct = Acct.objects.get(account_number=acct_number)
            AcctTran.objects.create_acct_tran(user, ae, acct, amount*(-1))

    def get_acct_number(self, discount=False):
        if discount:
            return 464400
        else:
            return 404400

    def auto_update_paid_object(self, request, payment):
        """
        Update the object after online payment is received.
        """
        if not request.user.profile.is_superuser:
            self.status_detail = 'paid - pending approval'
            self.save()

    def age(self):
        return datetime.now() - self.create_dt
    
    def cats_list(self):
        items = []
        for cat in self.cats.all():
            sub_cats = self.sub_cats.filter(parent=cat)
            items.append((cat, list(sub_cats)))
        return items

    @property
    def category_set(self):
        items = {}
        for cat in self.categories.select_related('category', 'parent'):
            if cat.category:
                items["category"] = cat.category
            elif cat.parent:
                items["sub_category"] = cat.parent
        return items

    def renew_window(self):
        days = get_setting('module', 'directories', 'renewaldays')
        days = int(days)
        if self.expiration_dt and datetime.now() + timedelta(days) > self.expiration_dt:
            return True
        else:
            return False
        
    def has_membership_with(self, this_user):
        """
        Check if this directory is associated with a membership or a corporate membership
        that this user owns. 
        
        Return ``True`` if this directory is associated with an active membership
        or corporate membership, and this_user owns the membership or is a representative
        of the corporate membership, or is the ``creator`` or ``owner`` of this directory.
        """
        [m] = self.membershipdefault_set.filter(status_detail='active')[:1] or [None]
        if m:
            if any([this_user==self.creator,
                   this_user==self.owner,
                   this_user==m.user]):
                return True

        if hasattr(self, 'corpprofile'):
            corp_membership = self.corpprofile.corp_membership
            if corp_membership and corp_membership.status_detail == 'active':
                if any([this_user==self.creator,
                       this_user==self.owner,
                       self.corpprofile.is_rep(this_user)]):
                    return True
        return False

    def get_owner_emails_list(self):
        """
        Returns a list of owner's email addresses.
        
        It's tricky because directory doesn't have a clear owner. 
        Since the owner field can be changed to whoever last edited, we'll
        check the creator, the email address field, member or reps if 
        it is created from memberships and corp memberships, respectively.
        """
        emails_list = []
        # creator
        if self.creator and validate_email(self.creator.email):
            emails_list.append(self.creator.email)

        # the email field  
        if validate_email(self.email):
            emails_list.append(self.email)

        # member
        [m] = self.membershipdefault_set.filter(status_detail='active')[:1] or [None]
        if m and validate_email(m.user.email):
            emails_list.append(m.user.email)

        # corp reps
        if hasattr(self, 'corpprofile'):
            corp_reps = self.corpprofile.reps.all()
            for rep in corp_reps:
                if validate_email(rep.user.email):
                    emails_list.append(rep.user.email)

        return list(set(emails_list))

    def get_corp_profile(self):
        if hasattr(self, 'corpprofile'):
            return self.corpprofile

    def get_corp_type(self):
        """
        Returns the corporate membership type that associates with the directory.
        """
        corp_profile = self.get_corp_profile()
        if corp_profile:
            corp_membership = corp_profile.corp_membership
            if corp_membership:
                return corp_membership.corporate_membership_type

    def get_membership(self):
        [membership] = list(self.membershipdefault_set.filter(status_detail='active'))[:1] or [None]
        return membership

    def get_member_type(self):
        """
        Returns the membership type that associates with the directory.
        """
        membership = self.get_membership()
        if membership:
            return membership.membership_type

    def is_owner(self, user_this):
        if not user_this or not user_this.is_authenticated:
            return False

        # is creator or owner
        if user_this == self.creator or user_this == self.owner:
            return True

        # is corp rep
        if hasattr(self, 'corpprofile'):
            if self.corpprofile.reps.filter(user__in=[user_this]):
                return True
        
        # member
        membership = self.get_membership()
        if membership and membership.user == user_this:
            return True
        
        return False

    @staticmethod
    def get_my_directories_filter(user, my_directories_only=False):
        if user.is_authenticated and my_directories_only:
            filter_or = ({'creator': user,
                         'owner': user,
                         'membershipdefault__user': user,
                         'corpprofile__reps__user': user})
            q_obj_or = reduce(operator.or_, [Q(**{key: value}
                        ) for key, value in filter_or.items()])
            return Directory.objects.filter(q_obj_or).filter(status=True,
                                status_detail__in=['active', 'pending', 'paid - pending approval'])

        return Directory.objects.none()

    def can_connect_from(self, directory_from=None, directory_from_cat=None):
        """
        Check if this directory can be connected from ``directory_from``.
        """
        affliated_cats = self.get_affliated_cats()
        if directory_from_cat:
            return directory_from_cat in affliated_cats
        
        if directory_from:
            for cat in directory_from.cats.all():
                if cat in affliated_cats:
                    return True
        return False

    def get_affliated_cats(self):
        """
        Get a list of categories that are allowed to connect with the categories of this directory.
        """
        affliated_cats = []
        for cat in self.cats.all():
            if hasattr(cat, 'connections'):
                if cat.connections.affliated_cats.count() > 0:
                    affliated_cats += list(cat.connections.affliated_cats.all())
        return affliated_cats

    def get_parent_cats(self):
        """
        Get a list of parent categories that this directory can associate to.
        """
        parent_cats = []
        for cat in self.cats.all():
            connections = cat.allowed_connections.all()
            for c in connections:
                if not c.cat in parent_cats:
                    parent_cats.append(c.cat)
        return parent_cats

    def get_list_affiliates(self):
        """
        Return a sorted list of list of affiliate directories, 
        grouped by category.
        ex: [(category_name, [d1, d2, ..]),...]
        """
        affiliates_dict = {}
        affliated_cats = self.get_affliated_cats()
        for affiliateship in Affiliateship.objects.filter(directory=self):
            affiliate = affiliateship.affiliate
            if affiliate.status_detail =='active':
                cat = affiliateship.connected_as
                if cat in affliated_cats:
                    if cat in affiliates_dict:
                        affiliates_dict[cat].append(affiliate)
                    else:
                        affiliates_dict[cat] = [affiliate]

        return sorted(list(affiliates_dict.items()), key=lambda item: item[0].position)

    def get_list_parent_directories(self):
        """
        Return a sorted list of list of parent directories, 
        grouped by category, 
        ex: [(category_name, [d1, d2, ..]),...]
        """
        parents_dict = {}
        parent_cats = self.get_parent_cats()
        for affiliateship in Affiliateship.objects.filter(affiliate=self):
            parent_d = affiliateship.directory
            if parent_d.status_detail =='active':
                connected_cat = affiliateship.connected_as
                for cat in parent_d.cats.all():
                    if cat in parent_cats and connected_cat in cat.connections.affliated_cats.all():
                        if cat in parents_dict:
                            parents_dict[cat].append(parent_d)
                        else:
                            parents_dict[cat] = [parent_d]

        return sorted(list(parents_dict.items()), key=lambda item: item[0].position)

    def allow_associate_by(self, user_this):
        """
        Check if user_this is allowed to submit affiliate requests.
        
        If the connection is limited to the allowed connection, 
        this user will need to have a valid membership with the
        membership type is in the allowed types. 
        """
        affliated_cats = self.get_affliated_cats()

        if affliated_cats:
            if user_this.is_superuser:
                return True

            # check if user_this is the owner of a directory with the category in affliated_cats
            for directory in Directory.objects.filter(cats__in=affliated_cats):
                if directory.is_owner(user_this):
                    return True

    def allow_approve_affiliations_by(self, user_this):
        """
        Check if user_this is allowed to approve affiliate requests.
        
        Superuser or the directory owner can approve.
        The directory owners include creator, owner, and associated corp reps.
        """
        if not user_this or not user_this.is_authenticated:
            return False

        if user_this.is_superuser:
            return True

        # is creator or owner
        if user_this == self.creator or user_this == self.owner:
            return True

        # is a corp rep
        if hasattr(self, 'corpprofile'):
            if self.corpprofile.reps.filter(user__in=[user_this]):
                return True

        return False

    def allow_reject_affiliations_by(self, user_this):
        """
        Check if user_this is allowed to reject affiliate requests.
        
        Superuser or the directory owner can reject.
        The directory owners include creator, owner, and associated corp reps.
        """
        return self.allow_approve_affiliations_by(user_this)



class Affiliateship(models.Model):
    directory = models.ForeignKey(Directory, related_name='affiliateship_directories',
                                      on_delete=models.CASCADE)
    affiliate = models.ForeignKey(Directory, related_name='affiliateship_affiliate_directories',
                                       on_delete=models.CASCADE)
    connected_as = models.ForeignKey(Category, null=True, related_name='cat_affiliateships',
                                       on_delete=models.CASCADE)
    create_dt = models.DateTimeField(_("Created On"), auto_now_add=True)
    creator = models.ForeignKey(User, null=True, default=None,
                                on_delete=models.SET_NULL,
                                editable=False)
 
    class Meta:
        unique_together = ('directory', 'affiliate', 'connected_as')
        verbose_name = _("Directory Affiliateship")
        ordering = ['directory', 'affiliate']
        app_label = 'directories'


class DirectoryPricing(models.Model):
    guid = models.CharField(max_length=40)
    duration = models.IntegerField(blank=True, choices=ADMIN_DURATION_CHOICES)
    regular_price =models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0)
    premium_price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0)
    regular_price_member = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0)
    premium_price_member = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0)
    show_member_pricing = models.BooleanField(default=False)
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="directory_pricing_creator",  null=True, on_delete=models.SET_NULL)
    creator_username = models.CharField(max_length=150, null=True)
    owner = models.ForeignKey(User, related_name="directory_pricing_owner", null=True, on_delete=models.SET_NULL)
    owner_username = models.CharField(max_length=150, null=True)
    status = models.BooleanField(default=True)

    class Meta:
#         permissions = (("view_directorypricing", _("Can view directory pricing")),)
        app_label = 'directories'

    def __str__(self):
        currency_symbol = get_setting('site', 'global', 'currencysymbol')
        price = "%s%s(R)/%s(P)" % (currency_symbol, self.regular_price, self.premium_price)
        return "%d days for %s" % (self.duration, price)

    def save(self, user=None, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid4())
            if user and user.id:
                self.creator=user
                self.creator_username=user.username
        if user and user.id:
            self.owner=user
            self.owner_username=user.username
        if not self.regular_price: self.regular_price = 0
        if not self.premium_price: self.premium_price = 0

        super(DirectoryPricing, self).save(*args, **kwargs)

    def get_price_for_user(self, user=AnonymousUser(), list_type='regular'):
        if not user.is_anonymous and user.profile.is_member:
            if list_type == 'regular':
                return self.regular_price_member
            else:
                return self.premium_price_member
        else:
            if list_type == 'regular':
                return self.regular_price
            else:
                return self.premium_price

