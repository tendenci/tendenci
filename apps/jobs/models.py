from django.db import models

from uuid import uuid1
from perms.models import AuditingBaseModel

class Jobs(AuditingBaseModel):
    guid = models.CharField(max_length=40, default=uuid1)
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    list_type = models.CharField(max_length=50)
    #invoice_id = models.ForeignKey(Invoice, blank=True, null=True)
    code = models.CharField(max_length=50) # internal job-code
    level = models.CharField(max_length=50) # e.g. regular, premium
    location = models.CharField(max_length=50)
    skills = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    education = models.TextField(blank=True)
    period = models.CharField(max_length=50)
    is_agency = models.BooleanField()
    percent_travel = models.IntegerField()

    # confused
    requested_duration = models.DecimalField(max_digits=18, decimal_places=0, blank=True)
    activation_dt = models.DateTimeField(null=True, blank=True)
    post_dt = models.DateTimeField(null=True, blank=True)
    start_dt = models.DateTimeField(null=True, blank=True)
    expiration_dt = models.DateTimeField(null=True, blank=True)

    payment_method = models.CharField(max_length=50)
    member_price = models.DecimalField(max_digits=20, decimal_places=2, blank=True)
    member_count = models.IntegerField(blank=True)
    non_member_price = models.DecimalField(max_digits=20, decimal_places=2, blank=True)
    non_member_count = models.IntegerField(blank=True)
    override_price = models.DecimalField(null=True, max_digits=20, decimal_places=2, blank=True)
    override_userid = models.IntegerField(null=True, blank=True)
    position_reports_to = models.CharField(max_length=200)
    salary_from = models.DecimalField(max_digits=20, decimal_places=2, blank=True)
    salary_to = models.DecimalField(max_digits=20, decimal_places=2, blank=True)
    #entity_id = models.ForeignKey(Entity, blank=True, null=True)
    computer_skills = models.TextField(blank=True)
    expertise = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    citizenship_required = models.BooleanField()
    security_clearance = models.BooleanField()
    is_offsite = models.BooleanField(blank=True)
    position_title = models.CharField(max_length=200)
    language = models.CharField(max_length=200)

