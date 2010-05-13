from django.db import models
from base.models import AuthorityBase

class Article(AuthorityBase):

    guid = models.CharField(max_length=50, unique=False, blank=True)
    timezone = models.CharField(max_length=5, blank=True)
    headline = models.CharField(max_length=200, blank=True)
    summary = models.TextField(blank=True)
    body = models.TextField(blank=True)
    source = models.CharField(max_length=300, blank=True)

    # creator first name and lastname
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    phone = models.CharField(max_length=50, blank=True)
    fax = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=120, blank=True)
    website = models.CharField(max_length=300, blank=True)

    # release dates do not have to be set
    release_dt = models.DateTimeField(null=True, blank=True)

    # might go away w/ permissions
    allow_anonymous_view = models.BooleanField()
    allow_site_user_view = models.BooleanField()
    allow_member_view = models.BooleanField()
    allow_anonymous_edit = models.BooleanField()
    allow_site_user_edit = models.BooleanField()
    allow_member_edit = models.BooleanField()

    create_dt = models.DateTimeField(auto_now_add=True)

    syndicate = models.BooleanField()
    featured = models.BooleanField()
    design_notes = models.TextField(blank=True)

    # for podcast feeds
    enclosure_url = models.CharField(max_length=500, blank=True)
    enclosure_type = models.CharField(max_length=120, blank=True)
    enclosure_length = models.IntegerField()

    not_official_content = models.BooleanField(blank=True)

    # meta information
    page_title = models.TextField(blank=True)
    meta_keywords = models.TextField(blank=True)
    meta_description = models.TextField(blank=True)

    def __unicode__(self):
        return self.headline


