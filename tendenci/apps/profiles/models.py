import uuid

from timezones.fields import TimeZoneField

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.contenttypes import generic

from tendenci.core.perms.models import TendenciBaseModel
from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.apps.profiles.managers import ProfileManager, ProfileActiveManager
from tendenci.apps.entities.models import Entity

from tendenci.libs.abstracts.models import Person, Identity, Address


# class Profile(Identity, Address):
#     pass


class Profile(Person):
    # relations
    guid = models.CharField(max_length=40)
    entity = models.ForeignKey(Entity, blank=True, null=True)
    pl_id = models.IntegerField(default=1)
    historical_member_number = models.CharField(_('historical member number'), max_length=50, blank=True)

    # profile meta data
    salutation = models.CharField(_('salutation'), max_length=15, 
        blank=True, choices=(('Mr.', 'Mr.'),('Mrs.', 'Mrs.'),
            ('Ms.', 'Ms.'),('Miss', 'Miss'),('Dr.', 'Dr.'),('Prof.', 'Prof.'),('Hon.', 'Hon.'),))
    initials = models.CharField(_('initials'), max_length=50, blank=True)
    display_name = models.CharField(_('display name'), max_length=120, blank=True)
    mailing_name = models.CharField(_('mailing name'), max_length=120, blank=True)
    company = models.CharField(_('company'), max_length=100, blank=True)
    position_title = models.CharField(_('position title'), max_length=50, blank=True)
    position_assignment = models.CharField(_('position assignment'), max_length=50, blank=True)
    sex = models.CharField(_('sex'), max_length=50, blank=True, choices=(('male', u'Male'),('female', u'Female')))
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
    education = models.CharField(_('education'), max_length=100, blank=True)
    student = models.IntegerField(_('student'), null=True, blank=True)
    remember_login = models.BooleanField(_('remember login'))
    exported = models.BooleanField(_('exported'))
    direct_mail = models.BooleanField(_('direct mail'), default=False)
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

    objects = ProfileManager()
    actives = ProfileActiveManager()

    class Meta:
        permissions = (("view_profile", "Can view profile"),)
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __unicode__(self):
        if hasattr(self, 'user'):
            return self.user.username

    @models.permalink
    def get_absolute_url(self):
        return ('profile', [self.user.username])

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

    def get_name(self):

        user = self.user

        name = "%s %s" % (user.first_name, user.last_name)
        name = name.strip()

        return self.display_name or name or user.email or user.username

    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())

        # match allow_anonymous_view with opposite of hide_in_search
        if self.hide_in_search:
            self.allow_anonymous_view = False
        else:
            self.allow_anonymous_view = True

        super(Profile, self).save(*args, **kwargs)

        try:
            from tendenci.addons.campaign_monitor.utils import update_subscription
            if hasattr(self, 'old_email') and getattr(self, 'old_email') != self.user.email:
                update_subscription(self, self.old_email)
                del self.old_email
        except ImportError:
            pass

    # if this profile allows view by user2_compare
    def allow_view_by(self, user2_compare):
        boo = False

        if user2_compare.is_superuser:
            boo = True
        else:
            if user2_compare == self.user:
                boo = True
            else:
                if self.creator == user2_compare or self.owner == user2_compare:
                    if self.status == 1:
                        boo = True
                else:
                    if user2_compare.has_perm('profiles.view_profile', self):
                        boo = True

        return boo

    # if this profile allows edit by user2_compare
    def allow_edit_by(self, user2_compare):
        if user2_compare.is_superuser:
            return True
        else:
            if user2_compare == self.user:
                return True
            else:
                if self.creator == user2_compare or self.owner == user2_compare:
                    if self.status == 1:
                        return True
                else:
                    if user2_compare.has_perm('profiles.change_profile', self):
                        return True
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
        memberships = self.user.group_member.all()
        return [membership.group for membership in memberships]

    def refresh_member_number(self):
        memberships = self.user.membershipdefault_set.filter(
            status=True, status_detail__iexact='active'
        )

        if memberships:
            self.member_number = memberships[0].member_number
        else:
            self.member_number = u''

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
        un = ' '.join(args[1:])             # concat args into one string
        un = re.sub('\s+', '_', un)       # replace spaces w/ underscores
        un = re.sub('[^\w.-]+', '', un)   # remove non-word-characters
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

        return un.lower()

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
                'password': pw or uuid.uuid1().get_hex()[:6],
            })

        user.first_name = fn
        user.last_name = ln
        user.email = em
        user.save()

        if created:
            Profile.objects.create_profile(user)

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
