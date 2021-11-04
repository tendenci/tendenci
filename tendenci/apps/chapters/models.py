from datetime import date
import uuid

from django.db.models import Q
from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from django.template.defaultfilters import slugify

from tendenci.libs.tinymce import models as tinymce_models
from tendenci.apps.pages.models import BasePage
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.chapters.managers import (ChapterManager,
                    ChapterMembershipTypeManager,
                    ChapterMembershipManager,
                    ChapterMembershipAppManager)
from tendenci.apps.chapters.module_meta import ChapterMeta
from tendenci.apps.user_groups.models import Group
from tendenci.apps.entities.models import Entity
from tendenci.apps.files.models import File
from tendenci.apps.base.fields import SlugField
from tendenci.apps.regions.models import Region
from tendenci.libs.abstracts.models import OrderingBaseModel
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.payments.models import PaymentMethod
from tendenci.apps.invoices.models import Invoice


class Chapter(BasePage):
    """
    Chapters module. Similar to Pages with extra fields.
    """
    slug = SlugField(_('URL Path'), unique=True)
    entity = models.OneToOneField(Entity, null=True,
                                  on_delete=models.SET_NULL,)
    mission = tinymce_models.HTMLField(null=True, blank=True)
    notes = tinymce_models.HTMLField(null=True, blank=True)
    sponsors =tinymce_models.HTMLField(blank=True, default='')
    featured_image = models.ForeignKey(File, null=True, default=None,
                              related_name='chapters',
                              help_text=_('Only jpg, gif, or png images.'),
                              on_delete=models.SET_NULL)
    contact_name = models.CharField(max_length=200, null=True, blank=True)
    contact_email = models.CharField(max_length=200, null=True, blank=True)
    join_link = models.CharField(max_length=200, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, blank=True, null=True, on_delete=models.SET_NULL)
    county = models.CharField(_('county'), max_length=50, blank=True)
    state = models.CharField(_('state'), max_length=50, blank=True, default='')

    perms = GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = ChapterManager()

    def __str__(self):
        return str(self.title)

    class Meta:
        app_label = 'chapters'

    def get_absolute_url(self):
        return reverse('chapters.detail', args=[self.slug])

    def get_meta(self, name):
        """
        This method is standard across all models that are
        related to the Meta model.  Used to generate dynamic
        meta information niche to this model.
        """
        return ChapterMeta().get_meta(self, name)

    def officers(self):
        return Officer.objects.filter(chapter=self).order_by('pk')
    
    def save(self, *args, **kwargs):
        if not self.id:
            setattr(self, 'entity', None)
            setattr(self, 'group', None)
            # auto-generate a group and an entity
            self._auto_generate_entity()
            self._auto_generate_group()

        photo_upload = kwargs.pop('photo', None)

        super(Chapter, self).save(*args, **kwargs)
        if photo_upload and self.pk:
            image = File(content_type=ContentType.objects.get_for_model(self.__class__),
                         object_id=self.pk,
                         creator=self.creator,
                         creator_username=self.creator_username,
                         owner=self.owner,
                         owner_username=self.owner_username)
            photo_upload.file.seek(0)
            image.file.save(photo_upload.name, photo_upload)
            image.save()

            self.featured_image = image
            self.save()

    def _auto_generate_group(self):
        if not (hasattr(self, 'group') and self.group):
            # create a group for this type
            group = Group()
            group.name = f'{self.title}'[:200]
            group.slug = slugify(group.name)
            # ensure uniqueness of the slug
            if Group.objects.filter(slug=group.slug).exists():
                tmp_groups = Group.objects.filter(slug__istartswith=group.slug)
                if tmp_groups:
                    t_list = [g.slug[len(group.slug):] for g in tmp_groups]
                    num = 1
                    while str(num) in t_list:
                        num += 1
                    group.slug = f'{group.slug}{str(num)}'
                    # group name is also a unique field
                    group.name = f'{group.name}{str(num)}'

            group.label = self.title
            group.type = 'distribution'
            group.email_recipient = self.creator and self.creator.email or ''
            group.show_as_option = False
            group.allow_self_add = False
            group.allow_self_remove = False
            group.show_for_memberships = False
            group.description = "Auto-generated with the chapter."
            group.notes = "Auto-generated with the chapter. Used for chapters only"
            #group.use_for_membership = 1
            group.creator = self.creator
            group.creator_username = self.creator_username
            group.owner = self.creator
            group.owner_username = self.owner_username
            group.entity = self.entity

            group.save()

            self.group = group

    def _auto_generate_entity(self):
        if not (hasattr(self, 'entity') and self.entity):
            # create an entity
            entity = Entity.objects.create(
                    entity_name=self.title[:200],
                    entity_type='Chapter',
                    email=self.creator and self.creator.email or '',
                    allow_anonymous_view=False)
            self.entity = entity

    def update_group_perms(self, **kwargs):
        """
        Update the associated group perms for the officers of this chapter. 
        Grant officers the view and change permissions for their own group.
        """
        if not self.group:
            return
 
        ObjectPermission.objects.remove_all(self.group)
    
        perms = ['view', 'change']

        officer_users = [officer.user for officer in self.officers(
            ).filter(Q(expire_dt__isnull=True) | Q(expire_dt__gte=date.today()))]
        if officer_users:
            ObjectPermission.objects.assign(officer_users,
                                        self.group, perms=perms)

    def is_chapter_leader(self, user):
        """
        Check if this user is one of the chapter leaders.
        """
        return self.officers().filter(Q(expire_dt__isnull=True) | Q(
            expire_dt__gte=date.today())).filter(user=user).exist()


class Position(models.Model):
    title = models.CharField(_(u'title'), max_length=200)

    class Meta:
        app_label = 'chapters'

    def __str__(self):
        return str(self.title)


class Officer(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    user = models.ForeignKey(User,  related_name="%(app_label)s_%(class)s_user", on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=120, null=True, blank=True)
    expire_dt = models.DateField(_('Expire Date'), blank=True, null=True,
                                 help_text=_('Leave it blank if never expires.'))

    class Meta:
        app_label = 'chapters'

    def __str__(self):
        return "%s" % self.pk


class ChapterMembershipType(OrderingBaseModel, TendenciBaseModel):
    PRICE_FORMAT = '%s - %s'
    ADMIN_FEE_FORMAT = ' (+%s admin fee)'
    RENEW_FORMAT = ' Renewal'
    PERIOD_CHOICES = (
        ("fixed", _("Fixed")),
        ("rolling", _("Rolling")),
    )
    PERIOD_UNIT_CHOICES = (
        ("days", _("Days")),
        ("months", _("Months")),
        ("years", _("Years")),
    )

    guid = models.CharField(max_length=50)
    name = models.CharField(_('Name'), max_length=255, unique=True)
    description = models.CharField(_('Description'), max_length=500)
    price = models.DecimalField(
        _('Price'),
        max_digits=15,
        decimal_places=2,
        blank=True,
        default=0,
        help_text=_("Set 0 for free membership.")
    )
    renewal_price = models.DecimalField(_('Renewal Price'), max_digits=15, decimal_places=2,
        blank=True, default=0, null=True, help_text=_("Set 0 for free membership."))

    require_approval = models.BooleanField(_('Require Approval'), default=True)
    require_payment_approval = models.BooleanField(
        _('Auto-approval requires payment'), default=True,
        help_text=_('If checked, auto-approved memberships will require a successful online payment to be auto-approved.'))
    allow_renewal = models.BooleanField(_('Allow Renewal'), default=True, help_text=_("If not selected, then this membership type cannot be renewed."))
    renewal = models.BooleanField(_('Renewal Only'), default=False, help_text=_("Reserve this membership type for renewals only, not available to new members."))
    renewal_require_approval = models.BooleanField(_('Renewal Requires Approval'), default=True)

    admin_only = models.BooleanField(_('Admin Only'), default=False)  # from allowuseroption

    never_expires = models.BooleanField(_("Never Expires"), default=False,
                                        help_text=_('If selected, skip the Renewal Options.'))
    period = models.IntegerField(_('Period'), default=0)
    period_unit = models.CharField(choices=PERIOD_UNIT_CHOICES, max_length=10)
    period_type = models.CharField(_("Period Type"), default='rolling', choices=PERIOD_CHOICES, max_length=10)

    rolling_option = models.CharField(_('Expires On'), max_length=50)
    rolling_option1_day = models.IntegerField(_('Expiration Day'), default=0)
    rolling_renew_option = models.CharField(_('Renewal Expires On'), max_length=50)
    rolling_renew_option1_day = models.IntegerField(default=0)
    rolling_renew_option2_day = models.IntegerField(default=0)

    fixed_option = models.CharField(_('Expires On'), max_length=50)
    fixed_option1_day = models.IntegerField(default=0)
    fixed_option1_month = models.IntegerField(default=0)
    fixed_option1_year = models.IntegerField(default=0)
    fixed_option2_day = models.IntegerField(default=0)
    fixed_option2_month = models.IntegerField(default=0)

    fixed_option2_can_rollover = models.BooleanField(_("Allow Rollover"), default=False)
    fixed_option2_rollover_days = models.IntegerField(default=0,
            help_text=_("Membership signups after this date covers the following calendar year as well."))

    renewal_period_start = models.IntegerField(_('Renewal Period Start'), default=30,
            help_text=_("How long (in days) before the memberships expires can the member renew their membership."))
    renewal_period_end = models.IntegerField(_('Renewal Period End'), default=30,
            help_text=_("How long (in days) after the memberships expires can the member renew their membership."))
    expiration_grace_period = models.IntegerField(_('Expiration Grace Period'), default=0,
            help_text=_("The number of days (maximum 100) after the membership expires their membership is still active."))

    objects = ChapterMembershipTypeManager()

    class Meta:
        verbose_name = _("Chapter Membership Type")
        app_label = 'chapters'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Save GUID if GUID is not set.
        Save MembershipType instance.
        """
        self.guid = self.guid or uuid.uuid4().hex
        super(ChapterMembershipType, self).save(*args, **kwargs)


class ChapterMembership(TendenciBaseModel):
    guid = models.CharField(max_length=50, editable=False)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    member_number = models.CharField(max_length=50, blank=True)
    membership_type = models.ForeignKey(ChapterMembershipType, on_delete=models.CASCADE)
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE)

    renewal = models.BooleanField(blank=True, default=False)
    certifications = models.CharField(max_length=500, blank=True, default='')
    work_experience = models.TextField(blank=True, default='')
    referral = models.CharField(max_length=500, blank=True, default='')
    expertise = models.CharField(max_length=1000, blank=True, default='')
    occupation = models.CharField(max_length=100, blank=True, default='')
    volunteer_availability = models.BooleanField(default=False)
    social_media_links = models.CharField(max_length=500, blank=True, default='')
    school_type = models.CharField(max_length=50, blank=True)
    school_name = models.CharField(max_length=200, blank=True, default='')
    
    ud1 = models.TextField(blank=True, default='')
    ud2 = models.TextField(blank=True, default='')
    ud3 = models.TextField(blank=True, default='')
    ud4 = models.TextField(blank=True, default='')
    ud5 = models.TextField(blank=True, default='')
    ud6 = models.TextField(blank=True, default='')
    ud7 = models.TextField(blank=True, default='')
    ud8 = models.TextField(blank=True, default='')
    ud9 = models.TextField(blank=True, default='')
    ud10 = models.TextField(blank=True, default='')
    ud11 = models.TextField(blank=True, default='')
    ud12 = models.TextField(blank=True, default='')
    ud13 = models.TextField(blank=True, default='')
    ud14 = models.TextField(blank=True, default='')
    ud15 = models.TextField(blank=True, default='')

    notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)

    join_dt = models.DateTimeField(_('Join Date'), blank=True, null=True)
    expire_dt = models.DateTimeField(_('Expire Date'), blank=True, null=True)
    renew_dt = models.DateTimeField(_('Renew Date'), blank=True, null=True)
    approved = models.BooleanField(default=False)
    approve_dt = models.DateTimeField(_('Approved Date'), blank=True, null=True)
    approved_user = models.ForeignKey(
        User, related_name='chaptermembership_approved_set', null=True,
        on_delete=models.SET_NULL)
    rejected = models.BooleanField(default=False)
    rejected_dt = models.DateTimeField(_('Rejected Date'), blank=True, null=True)
    rejected_user = models.ForeignKey(
        User, related_name='chaptermembership_rejected_set', null=True,
        on_delete=models.SET_NULL)

    payment_received_dt = models.DateTimeField(null=True)
    payment_method = models.ForeignKey(PaymentMethod, null=True,
                                       on_delete=models.SET_NULL)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)

    app = models.ForeignKey("ChapterMembershipApp", null=True, on_delete=models.SET_NULL)

    objects = ChapterMembershipManager()

    class Meta:
        verbose_name = _('Chapter Membership')
        verbose_name_plural = _('Chapter Memberships')
        app_label = 'chapters'

    def __str__(self):
        return f"Chapter Membership {self.pk} for {self.user.get_full_name()} in chapter {self.chapter}"

    def get_absolute_url(self):
        """
        Returns admin change_form page.
        """
        return reverse('chapter.membership_details', args=[self.pk])


class ChapterMembershipApp(TendenciBaseModel):
    guid = models.CharField(max_length=50, editable=False)

    name = models.CharField(_("Name"), max_length=155)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True,
        help_text=_("Description of this application. " +
        "Displays at top of application."))
    confirmation_text = tinymce_models.HTMLField()
    notes = models.TextField(blank=True, default='')
    use_captcha = models.BooleanField(_("Use Captcha"), default=True)
    membership_types = models.ManyToManyField(ChapterMembershipType,
                                        verbose_name="Chapter Membership Types")
    payment_methods = models.ManyToManyField(PaymentMethod,
                                             verbose_name=_("Payment Methods"))
    objects = ChapterMembershipAppManager()

    class Meta:
        verbose_name = _("Chapter Membership Application")
        app_label = 'chapters'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('membership_default.add', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid4())
        super(ChapterMembershipApp, self).save(*args, **kwargs)


class ChapterMembershipAppField(OrderingBaseModel):
    LABEL_MAX_LENGTH = 2000
    FIELD_TYPE_CHOICES1 = (
                    ("", _("Set to Default")),
                    ("CharField", _("Text")),
                    ("CharField/django.forms.Textarea", _("Paragraph Text")),
                    ("BooleanField", _("Checkbox")),
                    ("ChoiceField", _("Select One (Drop Down)")),
                    ("ChoiceField/django.forms.RadioSelect", _("Select One (Radio Buttons)")),
                    ("MultipleChoiceField", _("Multi select (Drop Down)")),
                    ("MultipleChoiceField/django.forms.CheckboxSelectMultiple", _("Multi select (Checkboxes)")),
                    ("CountrySelectField", _("Countries Drop Down")),
                    ("EmailField", _("Email")),
                    ("FileField", _("File upload")),
                    ("DateField/django.forms.widgets.SelectDateWidget", _("Date")),
                    ("DateTimeField", _("Date/time")),
                )
    FIELD_TYPE_CHOICES2 = (
                    ("section_break", _("Section Break")),
                )
    FIELD_TYPE_CHOICES = FIELD_TYPE_CHOICES1 + FIELD_TYPE_CHOICES2

    membership_app = models.ForeignKey("ChapterMembershipApp", related_name="fields", on_delete=models.CASCADE)
    label = models.CharField(_("Label"), max_length=LABEL_MAX_LENGTH)
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=100, blank=True, default='')
    required = models.BooleanField(_("Required"), default=False, blank=True)
    display = models.BooleanField(_("Show"), default=True, blank=True)
    customizable = models.BooleanField(default=False, blank=True,
                        help_text=_('Chapter leaders can customize this field.'))
    admin_only = models.BooleanField(_("Admin Only"), default=False)

    field_type = models.CharField(_("Field Type"), blank=True, choices=FIELD_TYPE_CHOICES,
                                  max_length=64)
    description = models.TextField(_("Description"),
                                   max_length=200,
                                   blank=True,
                                   default='')
    help_text = models.CharField(_("Help Text"),
                                 max_length=300,
                                 blank=True,
                                 default='')
    choices = models.CharField(_("Choices"), max_length=1000, blank=True,
        help_text=_("Comma separated options where applicable"))
    default_value = models.CharField(_("Default Value"),
                                     max_length=200,
                                     blank=True,
                                     default='')
    css_class = models.CharField(_("CSS Class"),
                                 max_length=200,
                                 blank=True,
                                 default='')

    class Meta:
        verbose_name = _("Field")
        verbose_name_plural = _("Fields")
        ordering = ('position',)
        app_label = 'chapters'

    def __str__(self):
        return str(self.id)
#         if self.field_name:
#             return f'{self.label} (field name: {self.field_name})'
#         return self.label

    @staticmethod
    def get_default_field_type(field_name):
        """
        Get the default field type for the ``field_name``.
        If the ``field_name`` is the name of one of the fields
        in User, Profile, MembershipDefault and MembershipDemographic
        models, the field type is determined via the field.
        Otherwise, default to 'CharField'.
        """
        available_field_types = [choice[0] for choice in
                                 ChapterMembershipAppField.FIELD_TYPE_CHOICES]
        fld = None
        field_type = 'CharField'

        chapter_membership_fields = dict([(field.name, field)
                        for field in ChapterMembership._meta.fields])
        if field_name in chapter_membership_fields:
            fld = chapter_membership_fields[field_name]

        if fld:
            field_type = fld.get_internal_type()
            if field_type not in available_field_types:
                if field_type in ['ForeignKey', 'OneToOneField']:
                    field_type = 'ChoiceField'
                elif field_type in ['ManyToManyField']:
                    field_type = 'MultipleChoiceField'
                else:
                    field_type = 'CharField'
        return field_type


class CustomizedAppField(models.Model):
    app_field = models.ForeignKey(ChapterMembershipAppField, related_name="customized_fields", on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    help_text = models.CharField(_("Help Text"),
                                 max_length=300,
                                 blank=True,
                                 default='')
    choices = models.CharField(_("Choices"), max_length=1000, blank=True,
        help_text=_("Comma separated options where applicable"))
    default_value = models.CharField(_("Default Value"),
                                     max_length=200,
                                     blank=True,
                                     default='')

    class Meta:
        unique_together = ('app_field', 'chapter',)


class ChapterMembershipFile(File):
    """
    This model will be used as handlers of File upload assigned
    to User Defined fields for Chapter Membership UD fields
    """
    class Meta:
        app_label = 'chapters'
