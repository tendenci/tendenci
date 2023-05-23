import subprocess
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.conf import settings
from django.contrib import messages

from tendenci.libs.utils import python_executable
from tendenci.apps.theme.templatetags.static import static
from .models import (SchoolCategory, Certification,
                     CertCat, Course, Transcript,
                     TeachingActivity,
                     OutsideSchool,
                     UserCertData,
                     Exam,
                     BluevoltExamImport)
from .forms import CourseForm, UpdateTranscriptActionForm


class TeachingActivityAdmin(admin.ModelAdmin):
    model = TeachingActivity
    list_display = ['id',
                    'user',
                    'activity_name',
                    'date',
                    'status_detail',]
    list_editable = ('status_detail', )
    search_fields = ['activity_name',
                     'user__first_name',
                     'user__last_name',
                     'user__email']
    list_filter = ['status_detail',]
    fieldsets = (
        (None, {
            'fields': (
            'user',
            'activity_name',
            'status_detail',
            'date',
            'description',
            
        )},),
    )
    
    autocomplete_fields = ('user',)

    class Media:
        css = {
            "all": (static("css/autocomplete_ext.css"),)
        }

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing
            return self.readonly_fields + ('user',)
        return self.readonly_fields


class OutsideSchoolAdmin(admin.ModelAdmin):
    model = OutsideSchool
    list_display = ['id',
                    'user',
                    'school_name',
                    'school_category',
                    'credits',
                    'certification_track',
                    'date',
                    'status_detail',]
    list_editable = ('school_category', 'credits', 'certification_track', 'status_detail', )
    search_fields = ['school_name',
                     'user__first_name',
                     'user__last_name',
                     'user__email']
    list_filter = ['status_detail',]
    list_per_page = 20
    #form = OutsideSchoolAdminForm
    fieldsets = (
        (None, {
            'fields': (
            'user',
            'school_name',
            'school_category',
            'date',
            'credits',
            'certification_track',
            'status_detail',
            'description',
            
        )},),
    )
    autocomplete_fields = ('user',)

    class Media:
        css = {
            "all": (static("css/autocomplete_ext.css"),)
        }

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing
            return self.readonly_fields + ('user',)
        return self.readonly_fields


class SchoolCategoryAdmin(admin.ModelAdmin):
    model = SchoolCategory
    list_display = ['id', 'name',
                    'status_detail',]


class CategoryAdminInline(admin.TabularInline):
    fieldsets = (
        (None, {
            'fields': (
            'category',
            'required_credits'
        )},),
    )
    extra = 0
    model = CertCat


class CertificationAdmin(admin.ModelAdmin):
    model = SchoolCategory
    list_display = ['id', 'name',
                    'period', 'enable_diamond']
    inlines = (CategoryAdminInline,)
    fieldsets = (
        (_(''), {
            'fields': ('name',
                       'period',
                       'enable_diamond',)
        }),
        (_('Diamond Requirements'), {'description':
                                     'Set requirements for each diamond',
                                     'classes': ('collapse',),
                                     'fields': (
            'diamond_name',
            'diamond_required_credits',
            'diamond_required_online_credits',
            'diamond_period',
            'diamond_required_activity'
        )}),)


class CourseAdmin(admin.ModelAdmin):
    model = Course
    list_display = ['id', 'name', 'course_code',
                    'location_type',
                    'school_category',
                    'credits',
                    'status_detail'
                    ]
    search_fields = ['name', 'location_type', 'course_code']
    list_filter = ['status_detail', 'location_type', 'school_category']
    fieldsets = (
        (_('General'), {
            'fields': ('name',
                       'location_type',
                       'school_category',
                       'course_code',
                       'summary',
                       'description',
                       'credits',
                       'min_score',
                       'status_detail',)
        }),
        (_('Permissions'), {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        )
    form = CourseForm


class ExamAdmin(admin.ModelAdmin):
    model = Exam
    list_display = ['id', 'show_user',
                    'show_course',
                    'date',
                    'grade',
                    ]
    search_fields = ['user__first_name',
                     'user__last_name',
                     'user__username',
                     'user__email']
    fieldsets = (
        (None, {
            'fields': (
            'user',
            'course',
            'date',
            'grade',
        )},),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing
            return self.readonly_fields + ('user', 'course', 'date')
        return self.readonly_fields

    def has_add_permission(self, request):
        return False
    
    @mark_safe
    def show_user(self, instance):
        if instance.user:
            name = instance.user.get_full_name()
            if not name:
                name = instance.user.username
            return '<a href="{0}" title="{1}">{1}</a>'.format(
                    reverse('profile', args=[instance.user.username]),
                    name
                )
        return ""
    show_user.short_description = 'User'
    show_user.admin_order_field = 'user__first_name'

    @mark_safe
    def show_course(self, instance):
        if instance.course:
            return '<a href="{0}" title="{1}">{1}</a>'.format(
                    reverse('admin:trainings_course_change', args=[instance.course.id]),
                    instance.course.name
                )
        return ""
    show_course.short_description = 'Course'
    show_course.admin_order_field = 'course__name'


def assign_cert_track_to_selected(modeladmin, request, queryset):
    try:
        cert_id = int(request.POST['cert'])
    except:
        cert_id = None
    if cert_id:
        cert = Certification.objects.get(id=cert_id)
        count = 0
        for transcript in queryset:
            transcript.certification_track = cert
            transcript.save()
            count += 1
        if count > 0:
            if count == 1:
                modeladmin.message_user(request, ("Successfully assigned certification track '%s' to %d row") % (cert, count,), messages.SUCCESS)
            else:
                modeladmin.message_user(request, ("Successfully assigned certification track '%s' to %d rows") % (cert, count,), messages.SUCCESS)
assign_cert_track_to_selected.short_description = 'Assign certification track to selected Transcripts'


class TranscriptAdmin(admin.ModelAdmin):
    model = Transcript
    list_display = ['id', 'edit_link', 'show_user', 'course', 'show_school',
                    'school_category',
                    'location_type',
                    'credits',
                    'certification_track',
                    'date',
                    'apply_to',
                    'status', 
                    ]
    list_display_links = ('edit_link',)
    search_fields = ['user__first_name',
                     'user__last_name',
                     'user__email',
                     'user__username',
                     'course__name']
    list_filter = ['certification_track', 'location_type', 'school_category', 'status',]
    fieldsets = (
        (None, {
            'fields': (
            'user',
            'school_category',
            'location_type',
            'credits',
            'date',
            'certification_track',
            'apply_to',
            'status',
        )},),
    )
    list_editable = ('certification_track', 'apply_to', 'status',)
    actions = [
        assign_cert_track_to_selected,
    ]
    action_form = UpdateTranscriptActionForm

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js',
             static('js/trainings_admin_action.js'),
        )

    def edit_link(self, obj):
        return "Edit"
    edit_link.short_description = _('edit')

    def has_add_permission(self, request):
        return False

    @mark_safe
    def show_school(self, instance):
        if instance.registrant_id:
            from tendenci.apps.events.models import Registrant
            [registrant] = Registrant.objects.filter(id=instance.registrant_id)[:1] or [None]
            if registrant:
                event = registrant.registration.event
                return '<a href="{0}" title="{1}">{1}</a>'.format(
                        reverse('event', args=[event.id]),
                        event.title,
                    )
        elif instance.parent_id and instance.location_type == 'outside':
            school_name = instance.get_school_name()
            outside_school_url = reverse('admin:trainings_outsideschool_change', args=[instance.parent_id])
            return f'<a href="{outside_school_url}" title="Outside school: {school_name}">{school_name}</a>'
        return ""
    show_school.short_description = 'School'

    # def show_course(self, instance):
    #     if instance.registrant_id:
    #         from tendenci.apps.events.models import Registrant
    #         [registrant] = Registrant.objects.filter(id=instance.registrant_id)[:1] or [None]
    #         if registrant:
    #             event = registrant.registration.event
    #             course = event.course
    #             return course.name
    #     return ""
    # show_course.short_description = 'Course'
    
    @mark_safe
    def show_user(self, instance):
        if instance.user:
            name = instance.user.get_full_name()
            if not name:
                name = instance.user.username
            return '<a href="{0}" title="{1}">{1}</a>'.format(
                    reverse('profile', args=[instance.user.username]),
                    name
                )
        return ""
    show_user.short_description = 'User'
    show_user.admin_order_field = 'user__first_name'


class UserCertDataAdmin(admin.ModelAdmin):
    model = UserCertData
    list_display = ['id',
                    'show_user',
                    'certification',
                    'certification_dt',
                    'diamond_1_dt',
                    'diamond_2_dt',
                    'diamond_3_dt',
                    'diamond_4_dt',
                    'diamond_5_dt',
                    'diamond_6_dt',
                    'diamond_7_dt',
                    'diamond_8_dt',
                    'diamond_9_dt',
                    'show_transcript']
    #list_editable = ('certification_dt', 'diamond_1_dt')
    search_fields = ['user__first_name',
                     'user__last_name',
                     'user__email']
    list_filter = ['certification',]
    fieldsets = (
        (None, {
            'fields': (
            'user',
            'certification',
            'certification_dt',
            'diamond_1_dt',
            'diamond_2_dt',
            'diamond_3_dt',
            'diamond_4_dt',
            'diamond_5_dt',
            'diamond_6_dt',
            'diamond_7_dt',
            'diamond_8_dt',
            'diamond_9_dt',
        )},),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing
            return self.readonly_fields + ('user',)
        return self.readonly_fields

    @mark_safe
    def show_user(self, instance):
        if instance.user:
            name = instance.user.get_full_name()
            if not name:
                name = instance.user.username
            return '<a href="{0}" title="{1}">{1}</a>'.format(
                    reverse('profile', args=[instance.user.username]),
                    name
                )
        return ""
    show_user.short_description = 'User'
    
    @mark_safe
    def show_transcript(self, instance):
        if instance.user:
            url = reverse('trainings.transcripts_user', args=[instance.user.id])
            return f'<a href="{url}" title="View Transcript">View Transcript</a>'
        return ""
    show_transcript.short_description = 'Transcript'


class BluevoltExamImportAdmin(admin.ModelAdmin):
    model = BluevoltExamImport
    list_display = ['id',
                    'date_from',
                    'date_to',
                    'num_inserted',
                    'status_detail',
                    'run_start_date',
                    'run_finish_date',
                    'run_by',]
    list_filter = ['status_detail',]
    # fieldsets = (
    #     (None, {
    #         'fields': (
    #         'date_from',
    #         'date_to',
    #         'status_detail',
    #         'result_detail'
    #
    #     )},),
    # )
    def save_model(self, request, obj, form, change):
        super(BluevoltExamImportAdmin, self).save_model(request, obj, form, change)
        if not change:
            obj.run_by = request.user
            obj.save()
            
            subprocess.Popen([python_executable(), "manage.py",
                              "import_bluevolt_exams",
                              "--import_id",
                              str(obj.id)])  
    
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        if object_id:
            extra_context['show_save'] = False
        return super().changeform_view(request, object_id, form_url, extra_context)
    
    def get_form(self, request, obj=None, **kwargs):
        if not obj: # add
            kwargs['fields'] = ['date_from', 'date_to']
        else: # change
            kwargs['fields'] = ['date_from', 'date_to', 'status_detail', 'result_detail']
        return super(BluevoltExamImportAdmin, self).get_form(request, obj, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing
            return self.readonly_fields + ('date_from', 'date_to', 'status_detail', 'result_detail',)
        return self.readonly_fields

    # def has_change_permission(self, request, obj=None):
    #     return False

    def show_result_detail(self, obj):
        return mark_safe(obj.result_detail)
    show_result_detail.short_description = 'Result detail'



admin.site.register(SchoolCategory, SchoolCategoryAdmin)
admin.site.register(Certification, CertificationAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Exam, ExamAdmin)
admin.site.register(Transcript, TranscriptAdmin)
admin.site.register(TeachingActivity, TeachingActivityAdmin)
admin.site.register(OutsideSchool, OutsideSchoolAdmin)
admin.site.register(UserCertData, UserCertDataAdmin)
if hasattr(settings, 'BLUEVOLT_API_KEY') and settings.BLUEVOLT_API_KEY:
    admin.site.register(BluevoltExamImport, BluevoltExamImportAdmin)
