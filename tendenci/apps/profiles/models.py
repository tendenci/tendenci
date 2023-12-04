from collections import OrderedDict
import os
import uuid
import hashlib
import re
from urllib.parse import urlencode
from PIL import Image
from io import BytesIO

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.files.storage import default_storage
from django.core.files import File
from django.conf import settings
from django.db import connection, ProgrammingError
from django.db.models import Max

from tendenci.apps.base.utils import create_salesforce_contact
from tendenci.apps.profiles.managers import ProfileManager, ProfileActiveManager
from tendenci.apps.entities.models import Entity
from tendenci.apps.base.models import BaseImport, BaseImportData
from tendenci.apps.base.utils import correct_filename
from tendenci.libs.abstracts.models import Person
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.theme.templatetags.static import static
from tendenci.apps.perms.utils import has_perm
from tendenci.apps.industries.models import Industry
#from tendenci.apps.user_groups.models import Group


ALLOWED_PHOTO_SIZES = [128, 56, 100, 80, 48]

# class Profile(Identity, Address):
#     pass

def profile_directory(instance, filename):
    filename = correct_filename(filename)
    m = hashlib.md5()
    m.update(instance.user.username.encode())

    hex_digest = m.hexdigest()[:8]

    return f'profiles/photos/{hex_digest}{instance.user.id}/{filename}'


class Profile(Person):

    SALUTATION_CHOICES = (
        ('Mr.', _('Mr.')),
        ('Mrs.', _('Mrs.')),
        ('Ms.', _('Ms.')),
        ('Miss', _('Miss')),
        ('Dr.', _('Dr.')),
        ('Prof.', _('Prof.')),
        ('Hon.', _('Hon.')),
    )

    SEX_CHOICES = (
        ('male', _(u'Male')),
        ('female', _(u'Female'))
    )

    # relations
    guid = models.CharField(max_length=40)
    account_id = models.IntegerField(blank=True, null=True, unique=True)
    entity = models.ForeignKey(Entity, blank=True, null=True, on_delete=models.SET_NULL)
    pl_id = models.IntegerField(default=1)
    historical_member_number = models.CharField(_('historical member number'), max_length=50, blank=True)

    # photo
    photo = models.ImageField(upload_to=profile_directory, blank=True, null=True)

    # profile meta data
    salutation = models.CharField(_('salutation'), max_length=15, blank=True, choices=SALUTATION_CHOICES)
    initials = models.CharField(_('initials'), max_length=50, blank=True)
    display_name = models.CharField(_('display name'), max_length=120, blank=True)
    mailing_name = models.CharField(_('mailing name'), max_length=120, blank=True)
    industry = models.ForeignKey(Industry, blank=True, null=True, on_delete=models.SET_NULL)
    company = models.CharField(_('company'), max_length=100, blank=True)
    position_title = models.CharField(_('position title'), max_length=250, blank=True)
    position_assignment = models.CharField(_('position assignment'), max_length=50, blank=True)
    sex = models.CharField(_('gender'), max_length=50, blank=True, choices=SEX_CHOICES)
    address_type = models.CharField(_('address type'), max_length=50, blank=True)
    phone2 = models.CharField(_('phone2'), max_length=50, blank=True)
    fax = models.CharField(_('fax'), max_length=50, blank=True)
    work_phone = models.CharField(_('work phone'), max_length=50, blank=True)
    home_phone = models.CharField(_('home phone'), max_length=50, blank=True)
    mobile_phone = models.CharField(_('mobile phone'), max_length=50, blank=True)
    # email in auth_user
    email2 = models.CharField(_('email2'), max_length=200,  blank=True)
    url2 = models.CharField(_('url2'), max_length=100, blank=True)
    dob = models.DateTimeField(_('date of birth'), null=True, blank=True)
    ssn = models.CharField(_('social security number'), max_length=50, blank=True)
    spouse = models.CharField(_('spouse'), max_length=50, blank=True)
    department = models.CharField(_('department'), max_length=50, blank=True)
    education = models.CharField(_('highest level of education'), max_length=100, blank=True)
    student = models.IntegerField(_('student'), null=True, blank=True)
    remember_login = models.BooleanField(_('remember login'), default=False)
    exported = models.BooleanField(_('exported'), default=False)
    direct_mail = models.BooleanField(_('direct mail'), default=True)
    notes = models.TextField(_('notes'), blank=True)
    admin_notes = models.TextField(_('admin notes'), blank=True)
    referral_source = models.CharField(_('referral source'), max_length=50, blank=True)
    hide_in_search = models.BooleanField(default=False)
    hide_address = models.BooleanField(default=False)
    hide_email = models.BooleanField(default=False)
    hide_phone = models.BooleanField(default=False)
    first_responder = models.BooleanField(_('first responder'), default=False)
    agreed_to_tos = models.BooleanField(_('agrees to tos'), default=False)
    original_username = models.CharField(max_length=50)
    
    # social media links
    linkedin = models.URLField(_('LinkedIn'), blank=True, default='')
    facebook = models.URLField(_('Facebook'), blank=True, default='')
    twitter = models.URLField(_('Twitter'), blank=True, default='')
    instagram = models.URLField(_('Instagram'), blank=True, default='')
    youtube = models.URLField(_('YouTube'), blank=True, default='')

    sf_contact_id = models.CharField(max_length=100, blank=True, null=True)

    # includes all invoice totals
    total_spend = models.DecimalField(_('total spend'), max_digits=16, decimal_places=4,
        default=0, editable=False)

    objects = ProfileManager()
    actives = ProfileActiveManager()

    class Meta:
#         permissions = (("view_profile", _("Can view profile")),)
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        app_label = 'profiles'

    def __str__(self):
        if hasattr(self, 'user'):
            return self.user.username
        else:
            return u''

    def __init__(self, *args, **kwargs):
        super(Profile, self).__init__(*args, **kwargs)
        self._original_photo = self.photo

    def get_absolute_url(self):
        from tendenci.apps.profiles.utils import clean_username
        cleaned_username = clean_username(self.user.username)
        if cleaned_username != self.user.username:
            self.user.username = cleaned_username
            self.user.save()
        return reverse('profile', args=[self.user.username])

    def _can_login(self):
        """
        Private function used to verify active statuses in
        user and profile records.
        """
        return all([self.user.is_active, self.status, self.status_detail == "active"])

    @property
    def is_active(self):
        return self._can_login()

    @property
    def is_member(self):
        if self.member_number and self._can_login():
            return True
        return False

    @property
    def is_staff(self):
        if self.is_superuser:
            return True
        return all([self._can_login(), self.user.is_staff])

    @property
    def is_superuser(self):
        return all([self._can_login(), self.user.is_superuser])

    @property
    def is_chapter_coordinator(self):
        return self.user.chapter_coordinators.exists()

    @property
    def lang(self):
        if self.language not in [l[0] for l in settings.LANGUAGES]:
            self.language = 'en'
            self.save()
        return self.language

    @property
    def has_released_credits(self):
        return self.released_credits.exists()

    @property
    def released_credits(self):
        """All released credits for this user"""
        from tendenci.apps.events.models import RegistrantCredits

        return RegistrantCredits.objects.filter(
            registrant__user=self.user, released=True).order_by('-credit_dt')

    @property
    def credits_grid(self):
        """
        Returns grid with credits by category -> by year -> by Event
        Also returns all credit names by category
        """
        credits = OrderedDict()
        credit_names_by_category = OrderedDict()

        for credit in self.released_credits:
            if not credit.event_credit:
                continue

            # Add category to grid
            category = credit.event_credit.ceu_subcategory.parent.name
            year = credit.credit_dt.year
            if category not in credits:
                credits[category] = OrderedDict()

            # Track credit names for this category across years
            credit_name = credit.event_credit.ceu_subcategory.name
            if category not in credit_names_by_category:
                credit_names_by_category[category] = list()

            # Add year to grid under current category
            if year not in credits[category]:
                credits[category][year] = {'total': 0, 'events': dict(), 'credits': OrderedDict()}

                # Add any credits from previous years in this category, initialize to 0
                for previous_years_credit in credit_names_by_category[category]:
                    credits[category][year]['credits'][previous_years_credit] = 0

            # If this is a new credit we've just seen this year, update previous years
            # with 0 credits
            if credit_name not in credit_names_by_category[category]:
                for key in credits[category]:
                    credits[category][key]['credits'][credit_name] = 0
                    credits[category][key]['credits'] = \
                        OrderedDict(sorted(credits[category][key]['credits'].items()))
                credit_names_by_category[category].append(credit_name)
                credit_names_by_category[category] = sorted(credit_names_by_category[category])

            # Update total credits for the year, and totals by credit
            credits[category][year]['total'] += credit.credits
            if credit_name not in credits[category][year]['credits']:
                credits[category][year]['credits'][credit_name] = 0
                credits[category][year]['credits'] = \
                    OrderedDict(sorted(credits[category][year]['credits'].items()))
            credits[category][year]['credits'][credit_name] += credit.credits

            # Add Event details for this year in this category
            event = credit.event
            if event.pk not in credits[category][year]['events']:
                credits[category][year]['events'][event.pk] = {
                    'start_dt': event.start_dt.strftime('%m-%d-%y'),
                    'credits': 0,
                    'type': category,
                    'meeting_name': event.parent.title if event.parent else event.title,
                    'registrant_id': credit.registrant.pk,
                    'event': event.title if event.parent else None,
                }

            # Update total credits for this event (by pk)
            credits[category][year]['events'][event.pk]['credits'] += credit.credits

        return credits, credit_names_by_category

    def first_name(self):
        return self.user.first_name

    def last_name(self):
        return self.user.last_name

    def username(self):
        return self.user.username

    def get_address(self):
        if self.address_type:
            return '%s (%s)' % (super(Profile, self).get_address(),
                                self.address_type)
        else:
            return super(Profile, self).get_address()

    def get_name(self):
        """
        Returns name first_name + last_name
        """
        user = self.user
        name = "%s %s" % (user.first_name, user.last_name)
        name = name.strip()

        return self.display_name or name or user.email or user.username

    def get_region_name(self):
        """
        Get the region name if the region field stores the value of region id.
        
        The region field is a char field in Profile. It is currently assigned
        on memberships join and edit as the value of a region id. So, the id
        needs to be converted to region_name to display on user profile. 
        """
        if self.region and self.region.isdigit():
            from tendenci.apps.regions.models import Region
            region_id = int(self.region)
            if Region.objects.filter(id=region_id).exists():
                region = Region.objects.get(id=region_id)
                return region.region_name
        return self.region

    def delete_old_photo(self):
        """
        Delete old photo and its cropped ones.
        """
        if self._original_photo:
            if default_storage.exists(self._original_photo.name):
                default_storage.delete(self._original_photo.name)
            head, tail = os.path.split(self._original_photo.name)
            for size in ALLOWED_PHOTO_SIZES:
                size_path = head + '/sizes/' + str(size) + '/' + tail
                if default_storage.exists(size_path):
                    default_storage.delete(size_path)

    def get_next_account_id(self):
        """
        Get the next available account_id.
        """
        account_id_max = Profile.objects.all().aggregate(Max('account_id'))['account_id__max']
        return account_id_max and account_id_max + 1 or 0

    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid4())

        # check and assign account id
        if not self.account_id and self.is_active:
            if get_setting('module', 'users', 'useaccountid'):
                self.account_id = self.get_next_account_id()
                self.save()

        # match allow_anonymous_view with opposite of hide_in_search
        if self.hide_in_search:
            self.allow_anonymous_view = False
        else:
            self.allow_anonymous_view = get_setting('module', 'users', 'allowanonymoususersearchuser')

        self.allow_user_view =  get_setting('module', 'users', 'allowusersearch')
        if get_setting('module', 'memberships', 'memberprotection') == 'private':
            self.allow_member_view = False
        else:
            self.allow_member_view = True

        super(Profile, self).save(*args, **kwargs)

        if self.photo and self._original_photo:
            if self._original_photo != self.photo:
                # remove existing photo from storage
                self.delete_old_photo()

        # try:
        #     from tendenci.apps.campaign_monitor.utils import update_subscription
        #     if hasattr(self, 'old_email') and getattr(self, 'old_email') != self.user.email:
        #         update_subscription(self, self.old_email)
        #         del self.old_email
        # except ImportError:
        #     pass

    def allow_search_users(self):
        """
        Check if this user can search users.
        """
        if self.is_superuser:
            return True

        # allow anonymous search users
        if get_setting('module', 'users', 'allowanonymoususersearchuser'):
            return True

        # allow user search users
        if get_setting('module', 'users', 'allowusersearch') \
            and self.user.is_authenticated:
            return True

        # allow members search users/members
        if get_setting('module', 'memberships', 'memberprotection') != 'private':
            if self.user.is_authenticated and self.user.profile.is_member:
                return True

        return False

    def allow_view_by(self, user2_compare):
        """
        Check if `user2_compare` is allowed to view this user.
        """
        # user2_compare is superuser
        if user2_compare.is_superuser:
            return True

        # this user is user2_compare self
        if user2_compare == self.user:
            return True

        # user2_compare is creator or owner of this user
        if (self.creator and self.creator == user2_compare) or \
            (self.owner and self.owner == user2_compare):
            if self.status:
                return True

        # user2_compare can search users and has view perm
        if user2_compare.profile.allow_search_users():
            if user2_compare.has_perm('profiles.view_profile', self):
                return True

        if has_perm(user2_compare, 'profiles.view_profile'):
            return True

        # chapter leaders can view
        for chapter_membership in self.chapter_memberships():
            if chapter_membership.chapter.is_chapter_leader(user2_compare):
                return True

        # False for everythin else
        return False

    def allow_edit_by(self, user2_compare):
        """
        Check if `user2_compare` is allowed to edit this user.
        """
        if user2_compare.is_superuser:
            return True

        if user2_compare == self.user:
            return True

        if (self.creator and self.creator == user2_compare) or \
            (self.owner and self.owner == user2_compare):
            if self.status:
                return True

        if user2_compare.has_perm('profiles.change_profile', self):
            return True

        # chapter leaders can edit
        for chapter_membership in self.chapter_memberships():
            if chapter_membership.chapter.is_chapter_leader(user2_compare):
                return True

        return False

    def allow_view_transcript(self, user2_compare):
        """
        Check if `user2_compare` is allowed to view this user's transcript.
        """
        if user2_compare.is_superuser:
            return True

        if user2_compare == self.user:
            return True
        
        if self.membership and self.membership.corp_profile_id:
            corp_profile_id = self.membership.corp_profile_id
            if user2_compare.corpmembershiprep_set.filter(corp_profile_id=corp_profile_id).exists():
                return True # user2_compare is a rep of the corp that this user is a member of

        return False

    def can_renew(self):
        """
        Looks at all memberships the user is actively associated
        with and returns whether the user is within a renewal period (boolean).
        """

        if not hasattr(self.user, 'memberships'):
            return False

        # look at active memberships

        active_memberships = self.user.memberships.filter(
            status=True, status_detail='active'
        )

        for membership in active_memberships:
            if membership.can_renew():
                return True

        return False

    def can_renew2(self):
        """
        Looks at all memberships the user is actively associated
        with and returns whether the user is within a renewal period (boolean).
        """

        if not hasattr(self.user, 'memberships'):
            return False

        # look at active memberships

        active_memberships = self.user.membershipdefault_set.filter(
            status=True, status_detail__iexact='active'
        )

        for membership in active_memberships:
            if membership.can_renew():
                return True

        return False

    def get_groups(self):
        memberships = self.user.group_member.filter(group__status=True)
        return [membership.group for membership in memberships]

    @property
    def membership(self):
        [membership] = self.user.membershipdefault_set.exclude(
                    status_detail='archive').order_by('-create_dt')[:1] or [None]
        return membership

    @property
    def chapter_membership(self):
        [chapter_membership] = self.chapter_memberships[:1] or [None]
        return chapter_membership
    
    def chapter_memberships(self):
        return self.user.chaptermembership_set.exclude(
               status_detail='archive').order_by('chapter', '-create_dt')

    def names_of_chapters(self):
        """
        Names of chapters that this user is a member of.
        """
        return ', '.join([m.chapter.title for m in self.chapter_memberships()]) 

    def get_chapters(self):
        """
        Get a list of chapters that this user is a member of.
        """
        chapters = set()
        chapter_memberships = self.user.chaptermembership_set.exclude(
               status_detail='archive')
        for cm in chapter_memberships:
            chapters.add(cm.chapter)
        return sorted(list(chapters), key=lambda c: c.title)

    def refresh_member_number(self):
        """
        Adds or removes member number from profile.
        """
        membership = self.user.membershipdefault_set.first(
            status=True, status_detail__iexact='active'
        )

        self.member_number = u''
        if membership:
            if not membership.member_number:
                membership.set_member_number()
                membership.save()
            self.member_number = membership.member_number

        self.save()
        return self.member_number

    @classmethod
    def spawn_username(*args):
        """
        Join arguments to create username [string].
        Find similiar usernames; auto-increment newest username.
        Return new username [string].
        """
        if not args:
            raise Exception('spawn_username() requires atleast 1 argument; 0 were given')

        import re

        max_length = 8
        # the first argument is the class, exclude it
        un = ''.join(args[1:])             # concat args into one string
        un =  un.lower()
        un = re.sub(r'\s+', '', un)       # remove spaces
        un = re.sub(r'[^\w.-]+', '', un)   # remove non-word-characters
        un = un.strip('_.- ')           # strip funny-characters from sides
        un = un[:max_length].lower()    # keep max length and lowercase username

        others = []  # find similiar usernames
        for u in User.objects.filter(username__startswith=un):
            if u.username.replace(un, '0').isdigit():
                others.append(int(u.username.replace(un, '0')))

        if others and 0 in others:
            # the appended digit will compromise the username length
            # there would have to be more than 99,999 duplicate usernames
            # to kill the database username max field length
            un = '%s%s' % (un, str(max(others) + 1))

        return un

    @classmethod
    def get_or_create_user(cls, **kwargs):
        """
        Return a user that's newly created or already existed.
        Return new or existing user.

        If username is passed.  It uses the username to return
        an existing user record or creates a new user record.

        If an email is passed.  It uses the email to return
        an existing user record or create a new user record.

        User is updated with first name, last name, and email
        address passed.

        If a password is passed; it is only used in order to
        create a new user account.
        """

        un = kwargs.get('username', u'')
        pw = kwargs.get('password', u'')
        fn = kwargs.get('first_name', u'')
        ln = kwargs.get('last_name', u'')
        em = kwargs.get('email', u'')

        user = None
        created = False

        if un:
            # created = False
            [user] = User.objects.filter(
                username=un)[:1] or [None]
        elif em:
            [user] = User.objects.filter(
                email=em).order_by('-pk')[:1] or [None]

        if not user:
            created = True
            user = User.objects.create_user(**{
                'username': un or Profile.spawn_username(fn[:1], ln),
                'email': em,
                'password': pw or uuid.uuid4().hex[:6],
            })

        user.first_name = fn
        user.last_name = ln
        user.email = em
        user.save()

        if created:
            profile = Profile.objects.create_profile(user)
            create_salesforce_contact(profile)  # Returns sf_id

        return user, created

    def roles(self):
        role_set = []

        if self.is_superuser:
            role_set.append('superuser')

        if self.is_staff:
            role_set.append('staff')

        if self.is_member:
            role_set.append('member')

        if self.is_active:
            role_set.append('user')

        return role_set or ['disabled']

    def highest_role(self):
        """
        The highest role will be returned.
        """
        roles = ['superuser', 'staff', 'member', 'user', 'disabled']
        for role in roles:
            if role in self.roles():
                return role

    def getMD5(self):
        m = hashlib.md5()
        m.update(self.user.email.encode())
        return m.hexdigest()

    def get_gravatar_url(self, size):
        if self.photo:
            photo_url = self.get_photo_url(size=size)
            if photo_url:
                return photo_url
        # Use old avatar, if exists, as the default
        default = ''
        if get_setting('module', 'users', 'useoldavatarasdefault'):
            c = connection.cursor()
            try:
                c.execute("select avatar from avatar_avatar where \"primary\"='t' and user_id=%d" % self.user.id)
                row = c.fetchone()
                if row and os.path.exists(os.path.join(settings.MEDIA_ROOT, row[0])):
                    default = '%s%s%s' %  (get_setting('site', 'global', 'siteurl'),
                                       settings.MEDIA_URL,
                                       row[0])
            except ProgrammingError:
                pass

            c.close()

        if not default:
            # Gravatar doesn't accept the url to the default image from an IP address,
            # as a result, it would show a broken avatar image.
            # Use Gravatar's own default image for sites not having domains yet
            site_url = get_setting('site', 'global', 'siteurl')
            if re.match(r'(http://|https://)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', site_url):
                default = ''
            else:
                default = '%s%s'%(site_url,
                                static(settings.GAVATAR_DEFAULT_URL))

        if get_setting('module', 'users', 'disablegravatar'):
            return default or static(settings.GAVATAR_DEFAULT_URL)

        gravatar_url = "//www.gravatar.com/avatar/" + self.getMD5() + "?"
        gravatar_url += urlencode({'d':default, 's':str(size)})
        return gravatar_url

    def get_photo_url(self, size=128):
        """
        Get the url of the photo with the size specified.
        """
        if not self.photo:
            return None

        if not size in ALLOWED_PHOTO_SIZES:
            # this size if not allowed, set it to default
            size = 128

        head, tail = os.path.split(self.photo.name)
        size_path = head + '/sizes/' + str(size) + '/' + tail

        if default_storage.exists(size_path):
            return default_storage.url(size_path)

        im = Image.open(default_storage.open(self.photo.name))
        im.thumbnail((size, size))

        #im.save(size_path)
        thumb_io = BytesIO()
        im.save(thumb_io, im.format)
        default_storage.save(size_path, File(thumb_io))

        return default_storage.url(size_path)

    def get_original_photo_url(self):
        if self.photo:
            return default_storage.url(self.photo.name)

    def two_factor_on(self):
        """
        Check if two-factor is on.
        """
        from two_factor.utils import default_device
        return default_device(self.user)

    def use_two_factor_auth(self):
        """
        Check if site uses two-factor authentication.
        """
        return settings.USE_TWO_FACTOR_AUTH

    def get_corp(self):
        """
        Get the corp profile (id and name only) that this user is a rep of.
        """
        corpmembershipreps = self.user.corpmembershiprep_set.filter(corp_profile__status=True)
        if corpmembershipreps.exists():
            return corpmembershipreps[0].corp_profile

        return None

def get_import_file_path(instance, filename):
    return "imports/profiles/{uuid}/{filename}".format(
                            uuid=uuid.uuid4().hex[:8],
                            filename=filename)


class UserImport(BaseImport):
    INTERACTIVE_CHOICES = (
        (True, _('Interactive')),
        (False, _('Not Interactive (no login)')),
    )

#     UPLOAD_DIR = "imports/profiles/%s" % uuid.uuid4().hex[:8]

    upload_file = models.FileField(_("Upload File"), max_length=260,
                                   upload_to=get_import_file_path,
                                   null=True)
    recap_file = models.FileField(_("Recap File"), max_length=260,
                                   null=True)

    interactive = models.BooleanField(choices=INTERACTIVE_CHOICES, default=False)
    exclude_is_active = models.BooleanField(_('Apply the above the Interactive/Non-interactive to new users ONLY.'),
                                            default=False)
    group_id = models.IntegerField(default=0)

    clear_group_membership = models.BooleanField(default=False)

    class Meta:
        app_label = 'profiles'

    def generate_recap(self):
        import csv
        if not self.recap_file and self.header_line:
            file_name = 'user_import_%d_recap.csv' % self.id
            file_path = '%s/%s' % (os.path.split(self.upload_file.name)[0],
                                   file_name)
            with default_storage.open(file_path, 'w') as f:
                recap_writer = csv.writer(f)
                header_row = self.header_line.split(',')
                if 'status' in header_row:
                    header_row.remove('status')
                if 'status_detail' in header_row:
                    header_row.remove('status_detail')
                header_row.extend(['action', 'error'])
                recap_writer.writerow(header_row)
                data_list = UserImportData.objects.filter(
                    uimport=self).order_by('row_num')
                for idata in data_list:
                    data_dict = idata.row_data
                    row = [data_dict[k] for k in header_row if k in data_dict]
                    row.extend([idata.action_taken, idata.error])
                    recap_writer.writerow(row)
            self.recap_file.name = file_path
            self.save()


class UserImportData(BaseImportData):
    uimport = models.ForeignKey(UserImport, related_name="user_import_data", on_delete=models.CASCADE)

    class Meta:
        app_label = 'profiles'
