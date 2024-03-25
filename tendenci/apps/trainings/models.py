from datetime import date
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse
from django.utils.functional import cached_property

from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.libs.tinymce import models as tinymce_models
from tendenci.apps.base.fields import DictField
from tendenci.apps.site_settings.utils import get_setting


class BluevoltExamImport(models.Model):
    date_from = models.DateField()
    date_to = models.DateField()
    
    num_inserted = models.PositiveIntegerField(blank=True, null=True,)
    status_detail = models.CharField(_('Status'),
                             max_length=10,
                             default='Pending')
    result_detail = models.TextField(blank=True, default='')
    run_by = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL,
        editable=False)
    run_start_date = models.DateTimeField(blank=True, null=True,)
    run_finish_date = models.DateTimeField(blank=True, null=True,)
    
    class Meta:
        verbose_name = _("Bluevolt Exam Import")
        verbose_name_plural = _("Bluevolt Exam Imports")
        app_label = 'trainings'

    def __str__(self):
        return f'Bluevolt import from {self.date_from} to {self.date_to}'


# class BluevoltCourseMap(models.Model):
#     bv_course_id = models.IntegerField(db_index=True)
#     course_id = models.IntegerField()
#
#
# class BluevoltUserMap(models.Model):
#     bv_user_id = models.IntegerField(db_index=True)
#     user_id = models.IntegerField()


class TeachingActivity(models.Model):
    STATUS_CHOICES = (
                ('pending', _('Pending')),
                ('approved', _('Approved')),
                ('disapproved', _('Disapproved')),
                )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_name = models.CharField(max_length=255,
                            db_index=True)
    date = models.DateField()
    description = models.TextField(blank=True, default='')
    create_dt = models.DateTimeField(_("Created On"), auto_now_add=True)
    update_dt = models.DateTimeField(_("Date"), auto_now=True)
    creator = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL,
        related_name="teaching_activities_created", editable=False)
    owner = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL,
        related_name="teaching_activities_updated")
    status_detail = models.CharField(_('Status'),
                             max_length=15,
                             default='pending',
                             choices=STATUS_CHOICES)
    
    def __str__(self):
        return self.activity_name

    class Meta:
        verbose_name = _("Teaching Activity")
        verbose_name_plural = _("Teaching Activities")
        app_label = 'trainings'


class OutsideSchool(models.Model):
    STATUS_CHOICES = (
                ('pending', _('Pending')),
                ('approved', _('Approved')),
                ('disapproved', _('Disapproved')),
                )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    school_name = models.CharField(max_length=255,
                            db_index=True)
    school_category = models.ForeignKey('SchoolCategory',
                                null=True, on_delete=models.SET_NULL)
    certification_track = models.ForeignKey('Certification',
                                   null=True, on_delete=models.SET_NULL)
    date = models.DateField()
    credits = models.DecimalField(max_digits=8, decimal_places=3, default=0)
    description = models.TextField(blank=True, default='')
    create_dt = models.DateTimeField(_("Created On"), auto_now_add=True)
    update_dt = models.DateTimeField(_("Date"), auto_now=True)
    creator = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL,
        related_name="outside_schools_created", editable=False)
    owner = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL,
        related_name="outside_schools_updated")
    status_detail = models.CharField(_('Status'),
                             max_length=15,
                             default='pending',
                             choices=STATUS_CHOICES)
    
    def __str__(self):
        return self.school_name

    class Meta:
        verbose_name = _("Outside School")
        verbose_name_plural = _("Outside Schools")
        app_label = 'trainings'


class SchoolCategory(models.Model):
    STATUS_CHOICES = (
                ('enabled', _('Enabled')),
                ('disabled', _('Disabled')),
                )
    name = models.CharField(_("Category Name"), max_length=150,
                             db_index=True, unique=True)
    status_detail = models.CharField(_('Status'),
                             max_length=10,
                             default='enabled',
                             choices=STATUS_CHOICES)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("School Category")
        verbose_name_plural = _("School Categories")
        app_label = 'trainings'


class Certification(models.Model):
    name = models.CharField(max_length=150, db_index=True, unique=True)
    period = models.PositiveSmallIntegerField()
    categories = models.ManyToManyField(SchoolCategory, through='CertCat')
    enable_diamond = models.BooleanField(default=False,
                                help_text=_("Enable diamond to be added"))
    diamond_name = models.CharField(max_length=50, blank=True, default='Diamond')
    diamond_required_credits = models.DecimalField(_("Required Credits"),
                                                   blank=True,
                                    max_digits=5, decimal_places=2, default=0)
    diamond_required_online_credits = models.DecimalField(_("Required Online Credits"),
                                                          blank=True, 
                                    max_digits=5, decimal_places=2, default=0)
    diamond_period = models.PositiveSmallIntegerField(_("Period"), blank=True, default=12)
    diamond_required_activity = models.PositiveSmallIntegerField(_("Required Teaching Activity"),
                                                                blank=True, default=1)
    required_credits = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        verbose_name = _("Certification")
        verbose_name_plural = _("Certifications")
        app_label = 'trainings'

    def __str__(self):
        return self.name

    def get_earned_credits(self, user, diamond_number=None, category=None, online_only=False):
        """
        Calculate the user earned credits.
        """
        #TODO: might need to include the credits from outside schools
        transcripts = user.transcript_set.filter(
                            certification_track=self,
                             status='approved')
        
        if diamond_number is not None:
            transcripts = transcripts.filter(apply_to=diamond_number,)

        if category:
            transcripts = transcripts.filter(school_category=category)
    
        if online_only:
            transcripts = transcripts.filter(location_type='online')
        
        return transcripts.aggregate(
                        Sum('credits'))['credits__sum'] or 0

    def is_requirements_met(self, user, diamond_number=0):
        """
        Check if the requirements is met to earn the certification
        or certain diamond (with diamond_number).
        """
        if not self.enable_diamond:
            # check required credits for each category
            cats = self.categories.all()
            for cat in cats:
                [certcat] = CertCat.objects.filter(certification=self, category=cat)[:1] or [None]
                if certcat:
                    required_credits = certcat.required_credits
                    earned_credits = self.get_earned_credits(user, category=cat)
                    if earned_credits < required_credits:
                        return False
        else:
            if diamond_number == 0:
                # check required credits for each category
                cats = self.categories.all()
                for cat in cats:
                    [certcat] = CertCat.objects.filter(certification=self, category=cat)[:1] or [None]
                    if certcat:
                        required_credits = certcat.required_credits
                        earned_credits = self.get_earned_credits(user,
                                                                 diamond_number=diamond_number,
                                                                 category=cat)
                        if earned_credits < required_credits:
                            return False
            else: # handle diamond
                # check required credits for diamond
                required_credits = self.diamond_required_credits
                earned_credits = self.get_earned_credits(user,
                                         diamond_number=diamond_number)
                if earned_credits < required_credits:
                    return False
    
                # check required online credits for diamond
                required_online_credits = self.diamond_required_online_credits
                earned_online_credits = self.get_earned_credits(user,
                                         diamond_number=diamond_number,
                                         online_only=True)
                if earned_online_credits < required_online_credits:
                    return False
    
                # check teaching activity is enough
                if self.diamond_required_activity:
                    count_teaching_activities = TeachingActivity.objects.filter(user=user).count()
    
                    if count_teaching_activities < self.diamond_required_activity * diamond_number:
                        # not enough teaching activities
                        return False

        return True

    def cert_required_credits(self, category=None):
        """
        Total required credits for the certification.
        """
        required_credits = 0
        cats = self.categories.all()
        if category:
            cats = cats.filter(id=category.id)
        for cat in cats:
            [certcat] = CertCat.objects.filter(certification=self, category=cat)[:1] or [None]
            if certcat:
                required_credits += certcat.required_credits
        return required_credits

    @cached_property
    def total_credits_required(self):
        return self.cert_required_credits()

    def cal_required_credits(self):
        """
        Calculate and update the required_credits for this certification.
        """
        total_credits_required = self.total_credits_required
        if self.required_credits != total_credits_required:
            self.required_credits = total_credits_required
            self.save(update_fields=['required_credits'])
       
    # def credits_earned_by_user(self, user, category=None, d_num=0, for_diamond_number=False):
    #     """
    #     Get credits earned and required by category for user
    #
    #     return a dictionary. Example: {
    #                                    cat1_id: {'credits_earned': 10,
    #                                             'credits_required': 20,},
    #                                    cat2_id: {'credits_earned': 30,
    #                                             'credits_required': 5,}
    #                                    } 
    #     """
    #     res = {}
    #
    #     cats = self.categories.all()
    #     if d_num == 0 and category:
    #         cats = cats.filter(id=category.id)
    #     for cat in cats:
    #         [certcat] = CertCat.objects.filter(certification=self, category=cat)[:1] or [None]
    #         if certcat:
    #             res[certcat.category.id] = {}
    #             res[certcat.category.id]['credits_earned'] = certcat.get_earned_credits(user, d_num=d_num, for_diamond_number=for_diamond_number)
    #             res[certcat.category.id]['credits_required'] = certcat.required_credits
    #     return res


    def diamonds_earned(self, user):
        """
        Check how many diamonds this user qualifies
        
        return num_diamonds, extra_credits_earned (for diamonds)
        """
        if not self.enable_diamond:
            return 0, 0
    
        cert_data, created = UserCertData.objects.get_or_create(
                                        user=user,
                                        certification=self)
        num_diamonds = cert_data.number_diamonds_earned()
        diamond_credits = user.transcript_set.filter(
                            certification_track=self,
                             status='approved').exclude(apply_to=0).aggregate(
                        Sum('credits'))['credits__sum'] or 0

        return num_diamonds, diamond_credits
        

    # def diamonds_earned0(self, user):
    #     """
    #     Check how many diamonds this user qualifies
    #
    #     return num_diamonds, extra_credits_earned (for diamonds)
    #     """
    #     if not self.enable_diamond:
    #         return 0, 0
    #
    #     required_credits, earned_credits = 0, 0
    #
    #     cats = self.categories.all()
    #     for cat in cats:
    #         [certcat] = CertCat.objects.filter(certification=self, category=cat)[:1] or [None]
    #         if certcat:
    #             required_credits += certcat.required_credits
    #             earned_credits += certcat.get_earned_credits(user)
    #
    #     if earned_credits >= required_credits:
    #         # user has earned more credits than required
    #         # now we can calculate the number of diamonds this user qualify
    #         extra_credits_earned = earned_credits - required_credits
    #         # ignore diamond_required_online_credits for now
    #         count_online_credits = Transcript.objects.filter(user=user,
    #                                  certification_track=self,
    #                                  location_type='online',
    #                                  status='approved'
    #                              ).aggregate(Sum('credits'))['credits__sum'] or 0
    #         count_teaching_activities = TeachingActivity.objects.filter(user=user).count()
    #         rc, roc, ra = 9, 9, 9 # why 9? because the maxmium diamonds one can get is 9
    #         if self.diamond_required_credits:
    #             # number of potential diamonds if required_credits meets 
    #             rc = extra_credits_earned // self.diamond_required_credits
    #         if self.diamond_required_online_credits:
    #             # number of potential diamonds if required_online_credits meets
    #             roc = count_online_credits // self.diamond_required_online_credits
    #         if self.diamond_required_activity:
    #             # number of potential diamonds if required_activity meets
    #             ra = count_teaching_activities // self.diamond_required_activity
    #
    #         num_diamonds = min(rc, roc, ra)
    #
    #         return num_diamonds, extra_credits_earned
    #
    #     return 0, 0   


class CertCat(models.Model):
    certification = models.ForeignKey(Certification, on_delete=models.CASCADE)
    category = models.ForeignKey(SchoolCategory, on_delete=models.CASCADE)
    required_credits = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.category.name} for {self.certification.name}'

    class Meta:
        unique_together = ('certification', 'category',)
        verbose_name = _("Certification Category")
        verbose_name_plural = _("Certification Categories")
        app_label = 'trainings'

    def get_earned_credits(self, user, d_num=None, for_diamond_number=False):
        """
        Get the user earned credits for this certification category.
        """
        return self.certification.get_earned_credits(user, 
                                                     diamond_number=d_num,
                                                     category=self.category)

    def save(self, *args, **kwargs):
        self.certification.cal_required_credits()
        super(CertCat, self).save(*args, **kwargs)
    

class Course(TendenciBaseModel):
    LOCATION_TYPE_CHOICES = (
                ('online', _('Online')),
                ('onsite', _('Onsite')),
                )
    STATUS_CHOICES = (
                ('enabled', _('Enabled')),
                ('disabled', _('Disabled')),
                )
    name = models.CharField(_("Course Name"), max_length=150,
                            db_index=True)
    location_type = models.CharField(_('Type'),
                             max_length=6,
                             default='online',
                             choices=LOCATION_TYPE_CHOICES)
    school_category = models.ForeignKey(SchoolCategory, null=True, on_delete=models.SET_NULL)
    course_code = models.CharField(max_length=50, blank=True, null=True)
    summary = models.TextField(blank=True, default='')
    description = tinymce_models.HTMLField(blank=True, default='')
    credits = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    min_score = models.PositiveSmallIntegerField(default=80)
    status_detail = models.CharField(_('Status'),
                             max_length=10,
                             default='enabled',
                             choices=STATUS_CHOICES)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")
        app_label = 'trainings'
    

class Exam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    grade = models.PositiveSmallIntegerField(default=0)
    date = models.DateField(null=True,)
    create_dt = models.DateTimeField(_("Created On"), auto_now_add=True)
    update_dt = models.DateTimeField(_("Date"), auto_now=True)
    creator = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL,
        related_name="trainings_exams_created", editable=False)
    owner = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL,
        related_name="trainings_exams_updated")
    
    def __str__(self):
        return f'Exam for {self.user} on {self.course}'

    class Meta:
        verbose_name = _("Exam")
        verbose_name_plural = _("Exams")
        app_label = 'trainings'


class Transcript(models.Model):
    # ex: online - BV courses
    #     onsite - events
    #     outside - outside schools
    LOCATION_TYPE_CHOICES = (
                ('online', _('Online')),
                ('onsite', _('Onsite')),
                ('outside', _('Outside')),
                )
    # APPLIED_CHOICES = (
    #             ('D', _('Designated')),
    #             ('C', _('Cancelled')),
    #             )
    STATUS_CHOICES = (
                ('pending', _('Pending')),
                ('approved', _('Approved')),
                ('cancelled', _('Cancelled')),
                )
    DIAMOND_CHOICES = ((x, x) for x in range(0, 10))
    parent_id = models.PositiveIntegerField(blank=True, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, null=True, on_delete=models.SET_NULL)
    course = models.ForeignKey(Course, null=True, on_delete=models.CASCADE)
    school_category = models.ForeignKey(SchoolCategory,
                                        null=True, on_delete=models.SET_NULL)
    location_type = models.CharField(_('Type'),
                             max_length=10,
                             default='online',
                             choices=LOCATION_TYPE_CHOICES)
    credits = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    # date added
    date = models.DateField(null=True)
    # applied = models.CharField(max_length=1, default='D',
    #                          choices=APPLIED_CHOICES)
    status = models.CharField(max_length=10, default='pending',
                             choices=STATUS_CHOICES)
    certification_track = models.ForeignKey(Certification,
                                   null=True, on_delete=models.SET_NULL)
    apply_to = models.IntegerField(_('Apply to diamond'), blank=True, default=0,
                                  choices=DIAMOND_CHOICES,
                                  help_text=_('Apply to a diamond number if applicable'))
    registrant_id = models.IntegerField(blank=True, default=0)
    external_id = models.CharField(max_length=50, default='')
    create_dt = models.DateTimeField(_("Created On"), auto_now_add=True)
    update_dt = models.DateTimeField(_("Last Updated"), auto_now=True)
    creator = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL,
        related_name="trainings_transcripts_created", editable=False)
    owner = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL,
        related_name="trainings_transcripts_updated")
    
    def __str__(self):
        return f'transcript for {self.user}'

    class Meta:
        verbose_name = _("Transcript")
        verbose_name_plural = _("Transcripts")
        app_label = 'trainings'

    def get_school_name(self):
        if self.parent_id and self.location_type == 'outside':
            [school_name] = OutsideSchool.objects.filter(id=self.parent_id,
                                         user=self.user
                                         ).values_list('school_name', flat=True)[:1] or ['']
            return school_name
        return ''

    def get_required_credits(self):
        [certcat] = CertCat.objects.filter(certification=self.certification_track,
                                           category=self.school_category)[:1] or [None]
        return certcat.required_credits if certcat else 0

    # def get_earned_credits_for_cat(self, d_num=0):
    #     """
    #     Calculate the user earned credits for the certification category.
    #     Exclude the current entry.
    #     """
    #     #TODO: may need to include the credits from outside schools
    #     transcripts = Transcript.objects.filter(user=self.user,
    #                          certification_track=self.certification_track,
    #                          school_category=self.school_category,
    #                          apply_to=d_num,
    #                          status='approved')
    #     if self.id:
    #         transcripts = transcripts.exclude(id=self.id)
    #
    #     return transcripts.aggregate(Sum('credits'))['credits__sum'] or 0
    
    def get_earned_credits(self, d_num=0, category_only=True, online_only=False, exclude_self=True):
        """
        Calculate the user earned credits.
         If category is provided, for the certification category.
        Exclude the current entry.
        
        Called by caculate_apply_to below
        """
        #TODO: may need to include the credits from outside schools
        transcripts = Transcript.objects.filter(user=self.user,
                             certification_track=self.certification_track,
                             apply_to=d_num,
                             status='approved')
        if category_only:
            transcripts = transcripts.filter(school_category=self.school_category)

        if online_only:
            transcripts = transcripts.filter(location_type='online')

        if exclude_self:
            transcripts = transcripts.exclude(id=self.id)
    
        return transcripts.aggregate(Sum('credits'))['credits__sum'] or 0

    def caculate_apply_to(self):
        """
        Caculate the value of apply_to (diamond number) to assign to this transcript entry.
        Due to lots of uncontrollable facts, this is just a best guess we can make.


        It first checks the largest diamond number that this user has earned so far 
        for this category. If the number is less than what's already recorded in the
         User Certification Data's table (UCD), use the one from UCD. Based on this 
         number, it then checks if credits earned is greater than credits required
         to determine whether this number should be added 1 before applying to the
         current entry.
        """
        if self.certification_track and self.certification_track.enable_diamond:
            if not self.apply_to:
                # Check what value to assign to among 0 - 9
                
                # if we're editing an old entry
                if self.apply_to == 0:
                    earned_credits = self.get_earned_credits(d_num=self.apply_to, category_only=True, online_only=False)
                    required_credits = self.certification_track.cert_required_credits(category=self.school_category)
                    if earned_credits < required_credits:
                        return 0

                # Step 1: Get the current max diamond number, and check what's already in UserCertData
                [max_apply_to] = Transcript.objects.filter(
                                     user=self.user,
                                     certification_track=self.certification_track,
                                     school_category=self.school_category
                                     ).values_list('apply_to', flat=True
                                                 ).order_by('-apply_to')[:1] or [0]
                # We'll need to respect the data already recorded in the UserCertData
                cert_data, created = UserCertData.objects.get_or_create(
                                        user=self.user,
                                        certification=self.certification_track)
                next_d_number = cert_data.get_next_d_number()

                # Step 2: If max_apply_to < next_d_number, set apply_to to next_d_number
                # Ex: If max_apply_to = 0, but user already has 1 diamond according to UserCertData,
                # then set max_apply_to to 2
                if  max_apply_to < next_d_number:
                    return next_d_number
                    #Transcript.objects.filter(id=self.id).update(apply_to=next_d_number)
                else:
                    # Step 3: Check required credits and earned credits for this category to decide what's the next value

                    if max_apply_to == 0: # certification not completed yet
                        earned_credits = self.get_earned_credits(d_num=max_apply_to, category_only=True, online_only=False)
                        required_credits = self.certification_track.cert_required_credits(category=self.school_category)
                        if earned_credits >= required_credits:
                            # user has earned enough credits for the cert, assign it to diamond 1
                            return max_apply_to + 1
                    else:
                        earned_credits = self.get_earned_credits(d_num=max_apply_to, category_only=False, online_only=False)
                        required_credits = self.certification_track.diamond_required_credits
    
                        if earned_credits >= required_credits:
                            # user has earned more credits than required for this diamond (with d_num=max_apply_to)
                            # also check online credits
                            if self.location_type == 'online':
                                earned_online_credits = self.get_earned_credits(d_num=max_apply_to, category_only=False, online_only=True)
                            
                                required_online_credits = self.certification_track.diamond_required_online_credits
                                # and user has earned more online credits than required
                                if earned_online_credits >= required_online_credits and max_apply_to < 9:
                                    # assign it to the next diamond
                                    return max_apply_to + 1
                            else:
                                # not online course, assign it to the next diamond
                                return max_apply_to + 1

                return max_apply_to
        return 0

    def save(self, *args, **kwargs):
        if not self.id:
            if not self.date:
                self.date = date.today()

            assign_diamond_number = kwargs.pop('assign_diamond_number', True)
            if assign_diamond_number and not self.apply_to:
                self.apply_to = self.caculate_apply_to()
        
        for cert in Certification.objects.all():
            user_cert_data = UserCertData.objects.filter(user=self.user, certification=cert).first()      
            if not user_cert_data:
                # add the user to UserCertData
                user_cert_data = UserCertData.objects.create(user=self.user, certification=cert)
            user_cert_data.cal_applicable_credits()
        super(Transcript, self).save(*args, **kwargs)


class UserCertData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    certification = models.ForeignKey(Certification,
                    on_delete=models.CASCADE)
    certification_dt = models.DateField(_('Certification Date'), null=True)
    diamond_1_dt = models.DateField(_('Diamond Date 1'), blank=True, null=True)
    diamond_2_dt = models.DateField(_('Diamond Date 2'), blank=True, null=True)
    diamond_3_dt = models.DateField(_('Diamond Date 3'), blank=True, null=True)
    diamond_4_dt = models.DateField(_('Diamond Date 4'), blank=True, null=True)
    diamond_5_dt = models.DateField(_('Diamond Date 5'), blank=True, null=True)
    diamond_6_dt = models.DateField(_('Diamond Date 6'), blank=True, null=True)
    diamond_7_dt = models.DateField(_('Diamond Date 7'), blank=True, null=True)
    diamond_8_dt = models.DateField(_('Diamond Date 8'), blank=True, null=True)
    diamond_9_dt = models.DateField(_('Diamond Date 9'), blank=True, null=True)
    applicable_credits = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.certification} for {self.user}'

    class Meta:
        unique_together = ('user', 'certification',)
        verbose_name = _("User Certification Data")
        verbose_name_plural = _("User Certification Data")
        app_label = 'trainings'

    def cal_applicable_credits(self):
        """
        Calculate and update the applicable_credits for this user's certification.
        """
        total_applicable_credits = 0
        for cat in self.certification.categories.all():
            [certcat] = CertCat.objects.filter(certification=self.certification, category=cat)[:1] or [None]
            if certcat:
                required_credits = certcat.required_credits
                earned_credits = self.certification.get_earned_credits(self.user, category=cat)
                if earned_credits > required_credits:
                    total_applicable_credits += required_credits
                else:
                    total_applicable_credits += earned_credits
        if total_applicable_credits != self.applicable_credits:
            self.applicable_credits = total_applicable_credits
            self.save(update_fields=['applicable_credits'])

    def get_next_d_number(self):
        if not self.certification_dt:
            return 0
        if not self.diamond_1_dt:
            return 1
        if not self.diamond_2_dt:
            return 2
        if not self.diamond_3_dt:
            return 3
        if not self.diamond_4_dt:
            return 4
        if not self.diamond_5_dt:
            return 5
        if not self.diamond_6_dt:
            return 6
        if not self.diamond_7_dt:
            return 7
        if not self.diamond_8_dt:
            return 8
        return 9

    def number_diamonds_earned(self):
        next_d_number = self.get_next_d_number()
        if next_d_number == 0 or (next_d_number == 9 and self.diamond_9_dt):
            return next_d_number
        else:
            return next_d_number - 1

    def email(self):
        return self.user.email

    @cached_property
    def total_credits(self):
        return self.user.transcript_set.filter(
                       certification_track=self.certification
                        ).filter(status='approved'
                                 ).aggregate(Sum('credits'))['credits__sum']


class UserCredit(UserCertData):
    class Meta:
        proxy = True
        verbose_name = "User Credits"
        verbose_name_plural = "User Credits"


def get_transcript_zip_file_path(instance, filename):
    return "export/trainings/{filename}".format(
                            filename=filename)


class CorpTranscriptsZipFile(models.Model):
    STATUS_CHOICES = (
        ("pending", _("Pending")),
        ("completed", _("Completed")),
        ("failed", _("Failed")),
    )
    # corp profile field
    corp_profile_id = models.IntegerField()
    params_dict = DictField(_('Parameters Dict'))
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    start_dt = models.DateTimeField(auto_now_add=True)
    finish_dt = models.DateTimeField(null=True, blank=True)
    zip_file = models.FileField(upload_to=get_transcript_zip_file_path)
    status = models.CharField(max_length=50,
                default="pending", choices=STATUS_CHOICES)

    @property
    def get_download_url(self):
        site_url = get_setting('site', 'global', 'siteurl')
        download_url = reverse('trainings.transcripts_corp_pdf_download', args=[self.pk])
        return f"{site_url}{download_url}"
    
    def get_corp_profile(self):
        from tendenci.apps.corporate_memberships.models import CorpProfile
        if CorpProfile.objects.filter(id=self.corp_profile_id).exists():
            return CorpProfile.objects.get(id=self.corp_profile_id)
        return None

    def delete(self, *args, **kwargs):
        if self.zip_file:
            self.zip_file.delete(save=False)
        super(CorpTranscriptsZipFile, self).delete(*args, **kwargs)  
