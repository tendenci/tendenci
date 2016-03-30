import requests

from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from tendenci.libs.tinymce import models as tinymce_models


ETHNICITY_CHOICES = (
    ('black', 'Black'),
    ('caucasian', 'Caucasian'),
    ('hispanic', 'Hispanic'),
    ('asian', 'Asian'),
    ('other', 'Other'),
)


class SkillSet(models.Model):
    '''
    A list of skills available to users
    '''
    user = models.OneToOneField(User)
    # Emergency Response Skills
    paramedic = models.BooleanField(_('paramedic'), default=False)
    fireman = models.BooleanField(_('fireman trained'), default=False)
    first_aid = models.BooleanField(_('first aid'), default=False)
    safety_manager = models.BooleanField(_('safety manager'), default=False)
    police = models.BooleanField(_('police'), default=False)
    search_and_rescue = models.BooleanField(_('search and rescue'), default=False)
    scuba_certified = models.BooleanField(_('scuba certified'), default=False)
    crowd_control = models.BooleanField(_('crowd control'), default=False)
    # Transportation Skills
    truck = models.BooleanField(_('truck driver'), default=False)
    pilot = models.BooleanField(_('pilot'), default=False)
    aircraft = models.CharField(_('aircraft'), max_length=100, blank=True, null=True)
    ship = models.BooleanField(_('ship captain'), default=False)
    sailor = models.BooleanField(_('sailor'), default=False)
    # Medical Skills
    doctor = models.BooleanField(_('medical doctor'), default=False)
    nurse = models.BooleanField(_('nurse'), default=False)
    medical_specialty = models.CharField(_('medical specialty'), max_length=100,
                                         blank=True, null=True)
    # Communication Skills
    crisis_communication = models.BooleanField(_('crisis communications'), default=False)
    media = models.BooleanField(_('media'), default=False)
    author = models.BooleanField(_('author'), default=False)
    public_speaker = models.BooleanField(_('public speaker'), default=False)
    politician = models.BooleanField(_('politician'), default=False)
    blogger = models.BooleanField(_('blogger'), default=False)
    photographer = models.BooleanField(_('photographer'), default=False)
    videographer = models.BooleanField(_('videographer'), default=False)
    radio_operator = models.BooleanField(_('radio operator'), default=False)
    call_sign = models.CharField(_('call sign'), max_length=100, blank=True, null=True)
    actor = models.BooleanField(_('actor'), default=False)
    thought_leader = models.BooleanField(_('thought leader'), default=False)
    influencer = models.BooleanField(_('influencer'), default=False)
    languages = models.CharField(_('languages spoken'), max_length=200, blank=True, null=True)
    # Education Skills
    teacher = models.BooleanField(_('teacher'), default=False)
    school_admin = models.BooleanField(_('school administrator'), default=False)
    # Military Skills
    military_rank = models.CharField(_('military rank'), max_length=100, blank=True, null=True)
    military_training = models.BooleanField(_('military training'), default=False)
    desert_trained = models.BooleanField(_('desert trained'), default=False)
    cold_trained = models.BooleanField(_('cold weather trained'), default=False)
    marksman = models.BooleanField(_('marksman'), default=False)
    security_clearance = models.CharField(_('security clearance'), max_length=200,
                                          blank=True, null=True)

    loc = models.PointField(blank=True, null=True)

    objects = models.GeoManager()

    def __unicode__(self):
        return '%s: Skills' % (self.user.profile.get_name())

    @property
    def is_first_responder(self):
        for field_name in self._meta.get_all_field_names():
            field = self._meta.get_field_by_name(field_name)[0]
            if isinstance(field, models.BooleanField):
                if getattr(self, field_name):
                    return True
        return False

    def save(self, *args, **kwargs):
        params = {'format': 'json',
                  'street': self.user.profile.address,
                  'city': self.user.profile.city,
                  'country': self.user.profile.country}
        url = 'http://nominatim.openstreetmap.org/search'
        result = requests.get(url, params=params).json()
        if result:
            lat = result[0]['lat']
            lng = result[0]['lon']
            self.loc = "POINT(%s %s)" % (lng, lat)
        super(SkillSet, self).save(*args, **kwargs)


class ReliefAssessment(models.Model):
    user = models.ForeignKey(User)
    # Additional Personal Information
    id_number = models.CharField(_('ID number'), max_length=50, blank=True, null=True)
    issuing_authority = models.CharField(_('issuing authority'), max_length=100,
                                         blank=True, null=True)
    health_insurance = models.BooleanField(_('health insurance'), default=False)
    insurance_provider = models.CharField(_('insurance provider'), max_length=100,
                                          blank=True, null=True)
    # Disaster Area Address
    address = models.CharField(_('address'), max_length=150)
    address2 = models.CharField(_('address2'), max_length=100, blank=True, null=True)
    city = models.CharField(_('city'), max_length=50)
    state = models.CharField(_('state'), max_length=50)
    zipcode = models.CharField(_('ZIP'), max_length=50)
    country = models.CharField(_('country'), max_length=50)
    # Alternate Address
    alt_address = models.CharField(_('address'), max_length=150, blank=True, null=True)
    alt_address2 = models.CharField(_('address2'), max_length=100, blank=True, null=True)
    alt_city = models.CharField(_('city'), max_length=50, blank=True, null=True)
    alt_state = models.CharField(_('state'), max_length=50, blank=True, null=True)
    alt_zipcode = models.CharField(_('ZIP'), max_length=50, blank=True, null=True)
    alt_country = models.CharField(_('country'), max_length=50, blank=True, null=True)
    # Ethnicity
    ethnicity = models.CharField("", max_length=10, choices=ETHNICITY_CHOICES,
                                 blank=True, null=True)
    other_ethnicity = models.CharField("", max_length=50, blank=True, null=True,
                                       help_text="Specify here if your ethnicity is not included above.")
    # Household
    below_2 = models.IntegerField(_('0 - 2 yrs'), blank=True, null=True)
    between_3_11 = models.IntegerField(_('3 - 11 yrs'), blank=True, null=True)
    between_12_18 = models.IntegerField(_('12 - 18 yrs'), blank=True, null=True)
    between_19_59 = models.IntegerField(_('19 - 59 yrs'), blank=True, null=True)
    above_60 = models.IntegerField(_('over 60 yrs'), blank=True, null=True)
    # Services
    ssa = models.BooleanField(_('social security administration'), default=False,
                              help_text="current recipient of Social Security")
    dhs = models.BooleanField(_('department human services'), default=False,
                              help_text="food stamps, WIC, TANF")
    children_needs = models.BooleanField(
        _('children needs'), default=False,
        help_text="school supplies, uniforms, clothing, child care, diapers, wipes")
    toiletries = models.BooleanField(_('toiletries'), default=False)
    employment = models.BooleanField(_('employment'), default=False)
    training = models.BooleanField(_('training'), default=False)
    food = models.BooleanField(_('food'), default=False)
    gas = models.BooleanField(_('gas'), default=False)
    prescription = models.BooleanField(_('prescription care'), default=False)
    other_service = models.CharField(_('other'), max_length=100, blank=True, null=True,
                                     help_text="Specify additional services needed.")
    # Internal
    case_notes = tinymce_models.HTMLField(_('case notes'), blank=True, null=True)
    items_provided = tinymce_models.HTMLField(_('items provided'), blank=True, null=True)

    loc = models.PointField(blank=True, null=True)

    objects = models.GeoManager()

    @models.permalink
    def get_absolute_url(self):
        return ('social-services.relief_area', [self.pk])

    def get_ethnicity(self):
        if self.ethnicity == 'other':
            return self.other_ethnicity
        return self.ethnicity

    def get_address(self):
        return "%s %s %s, %s %s %s" % (
            self.address, 
            self.address2, 
            self.city, 
            self.state, 
            self.zipcode,
            self.country
        )

    def save(self, *args, **kwargs):
        params = {'format': 'json',
                  'street': self.address,
                  'city': self.city,
                  'country': self.country}
        url = 'http://nominatim.openstreetmap.org/search'
        result = requests.get(url, params=params).json()
        if result:
            lat = result[0]['lat']
            lng = result[0]['lon']
            self.loc = "POINT(%s %s)" % (lng, lat)
        super(ReliefAssessment, self).save(*args, **kwargs)
