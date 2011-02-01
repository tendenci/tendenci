from django.db import models


class LegacyAbstractUserModel(models.Model):
    """
    Abstract Users Model from Legacy Tendenci
    """
    userid = models.AutoField(primary_key=True)
    guid = models.CharField(max_length=50, blank=True)
    usertypeid = models.IntegerField(null=True, blank=True)
    usertype = models.TextField(blank=True)
    entityid = models.IntegerField(null=True, blank=True)
    plid = models.IntegerField(null=True, blank=True)
    entityownerid = models.IntegerField(null=True, blank=True)
    memberid = models.TextField(blank=True)
    timezone = models.TextField(blank=True)
    lang = models.TextField(blank=True)
    firstname = models.CharField(max_length=100, blank=True)
    lastname = models.CharField(max_length=100, blank=True)
    initials = models.CharField(max_length=50, blank=True)
    loginname = models.CharField(max_length=50, blank=True)
    displayname = models.CharField(max_length=120, blank=True)
    mailingname = models.CharField(max_length=120, blank=True)
    company = models.CharField(max_length=100, blank=True)
    dunsno = models.CharField(max_length=50, blank=True)
    title = models.TextField(blank=True)
    positiontitle = models.CharField(max_length=50, blank=True)
    positionassignment = models.TextField(blank=True)
    sex = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=150, blank=True)
    address2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zipcode = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    county = models.CharField(max_length=50, blank=True)
    addresstype = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    phone2 = models.CharField(max_length=50, blank=True)
    fax = models.CharField(max_length=50, blank=True)
    workphone = models.CharField(max_length=50, blank=True)
    homephone = models.CharField(max_length=50, blank=True)
    mobilephone = models.CharField(max_length=50, blank=True)
    pager = models.CharField(max_length=50, blank=True)
    email = models.TextField(blank=True)
    email2 = models.TextField(blank=True)
    url = models.CharField(max_length=100, blank=True)
    url2 = models.CharField(max_length=100, blank=True)
    dob = models.TextField(blank=True) # This field type is a guess.
    ssn = models.CharField(max_length=50, blank=True)
    spouse = models.CharField(max_length=50, blank=True)
    department = models.CharField(max_length=50, blank=True)
    education = models.TextField(blank=True)
    student = models.IntegerField(null=True, blank=True)
    username = models.CharField(max_length=50, blank=True)
    password = models.CharField(max_length=50, blank=True)
    submitdate = models.TextField(blank=True) # This field type is a guess.
    securitylevel = models.CharField(max_length=50, blank=True)
    rememberlogin = models.NullBooleanField(blank=True)
    exported = models.NullBooleanField(blank=True)
    sessionid = models.CharField(max_length=50, blank=True)
    lastlogon = models.TextField(blank=True) # This field type is a guess.
    directmail = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True) # This field type is a guess.
    adminnotes = models.TextField(blank=True) # This field type is a guess.
    interactive = models.IntegerField(null=True, blank=True)
    referralsource = models.CharField(max_length=50, blank=True)
    ud1 = models.TextField(blank=True)
    ud2 = models.TextField(blank=True)
    ud3 = models.TextField(blank=True)
    ud4 = models.TextField(blank=True)
    tscore = models.FloatField(null=True, blank=True)
    damper = models.FloatField(null=True, blank=True)
    hits = models.IntegerField(null=True, blank=True)
    fancyhits = models.IntegerField(null=True, blank=True)
    tscoredatetime = models.TextField(blank=True) # This field type is a guess.
    createdatetime = models.TextField(blank=True) # This field type is a guess.
    creatoruserid = models.IntegerField(null=True, blank=True)
    creatorusername = models.CharField(max_length=50, blank=True)
    owneruserid = models.IntegerField(null=True, blank=True)
    owneruserid2 = models.IntegerField(null=True, blank=True)
    ownerusername = models.CharField(max_length=50, blank=True)
    status = models.IntegerField(null=True, blank=True)
    hideinsearch = models.NullBooleanField(blank=True)
    hideaddress = models.NullBooleanField(blank=True)
    hideemail = models.NullBooleanField(blank=True)
    hidephone = models.NullBooleanField(blank=True)
    articlespermissions = models.IntegerField(null=True, blank=True)
    calendareventspermissions = models.IntegerField(null=True, blank=True)
    catalogspermissions = models.IntegerField(null=True, blank=True)
    contentmanagerspermissions = models.IntegerField(null=True, blank=True)
    coursespermissions = models.IntegerField(null=True, blank=True)
    forumspermissions = models.IntegerField(null=True, blank=True)
    jobspermissions = models.IntegerField(null=True, blank=True)
    membershipspermissions = models.IntegerField(null=True, blank=True)
    releasespermissions = models.IntegerField(null=True, blank=True)
    resumespermissions = models.IntegerField(null=True, blank=True)
    surveyspermissions = models.IntegerField(null=True, blank=True)
    usergroupspermissions = models.IntegerField(null=True, blank=True)
    historicalmemberid = models.CharField(max_length=50, blank=True)
    firstresponder = models.NullBooleanField(blank=True)
    functionaltitleid = models.IntegerField(null=True, blank=True)
    author = models.IntegerField(null=True, blank=True)
    lastupdatedatetime = models.TextField(blank=True) # This field type is a guess.
    salutation = models.CharField(max_length=15, blank=True)
    directoriespermissions = models.IntegerField(null=True, blank=True)
    icon = models.TextField(blank=True)
    ballotspermissions = models.IntegerField(null=True, blank=True)
    openid = models.TextField(blank=True)
    customdisplayview = models.NullBooleanField(blank=True)
    statusdetail = models.TextField(blank=True)
    newsletterpermissions = models.IntegerField(null=True, blank=True)
    agreedtotos = models.NullBooleanField(blank=True)

    class Meta:
        abstract = True


class LegacyUserManager(models.Manager):
    """
    Manager that sets the default database for tendenci users
    """
    def __init__(self):
        super(LegacyUserManager, self).__init__()
        self._db = 'tendenci_legacy'


class LegacyUser(LegacyAbstractUserModel):
    """
    Auto Generated model from Legacy Tendenci
    """
    objects = LegacyUserManager()

    class Meta:
        managed = False # django should not manage this database table
        db_table = u'users'


class SchipulEmployeeManager(models.Manager):
    """
    Manager that sets the default database for tendenci users
    """
    def __init__(self):
        super(SchipulEmployeeManager, self).__init__()
        self._db = 'tendenci_master'


class SchipulEmployee(LegacyAbstractUserModel):
    """
     Auto Generated model from Legacy Tendenci
    """
    objects = SchipulEmployeeManager()
    
    class Meta:
        managed = False # django should not manage this database table
        db_table = u'schipulemployees'

