from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.encoding import iri_to_uri
from django.conf import settings

from event_logs.models import EventLog
from perms.utils import update_perms_and_save

from courses.models import Course, Question, Answer, CourseAttempt
from courses.forms import CourseForm

class CourseAttemptAdmin(admin.ModelAdmin):
    list_display = ['course', 'user', 'score', 'create_dt']
    
class AnswerInline(admin.StackedInline):
    model = Answer
    
class QuestionAdmin(admin.ModelAdmin):
    inlines = [
        AnswerInline,
    ]

class QuestionInline(admin.TabularInline):
    model = Question

class CourseAdmin(admin.ModelAdmin):
    inlines = [
        QuestionInline,
    ]
    list_display = ['title', 'deadline', 'passing_score', 'status', 'view_on_site']
    list_filter = []
    search_fields = []
    fieldsets = (
        (None, 
            {'fields': (
                'title',
                'content',
                'retries',
                'retry_interval',
                'passing_score',
                'deadline',
                'tags',
            )}
        ),
        ('Permissions', {'fields': ('allow_anonymous_view',)}),
        ('Advanced Permissions', {'classes': ('collapse',),'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        ('Publishing Status', {'fields': (
            'status',
            'status_detail'
        )}),
    )
    form = CourseForm
    actions = []

    class Media:
        js = (
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )

    def edit_link(self, obj):
        link = '<a href="%s" title="edit">Edit</a>' % reverse('admin:courses_course_change', args=[obj.pk])
        return link
    edit_link.allow_tags = True
    edit_link.short_description = 'edit'

    def view_on_site(self, obj):
        link_icon = '%simages/icons/external_16x16.png' % settings.STATIC_URL
        link = '<a href="%s" title="%s"><img src="%s" /></a>' % (
            reverse('courses.detail', args=[obj.pk]),
            obj,
            link_icon,
        )
        return link
    view_on_site.allow_tags = True
    view_on_site.short_description = 'view'

    def log_deletion(self, request, object, object_repr):
        super(CourseAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 555300,
            'event_data': '%s (%d) deleted by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)           

    def log_change(self, request, object, message):
        super(CourseAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 555200,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)               

    def log_addition(self, request, object):
        super(CourseAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 555100,
            'event_data': '%s (%d) added by %s' % (object._meta.object_name, 
                                                   object.pk, request.user),
            'description': '%s added' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)
                     
    def get_form(self, request, obj=None, **kwargs):
        """
        inject the user in the form.
        """
        form = super(CourseAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def save_model(self, request, object, form, change):
        """
        update the permissions backend
        """
        instance = form.save(commit=False)
        perms = update_perms_and_save(request, form, instance)
        return instance

    def change_view(self, request, object_id, extra_context=None):
        result = super(CourseAdmin, self).change_view(request, object_id, extra_context)

        if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue') and request.GET.has_key('next'):
            result['Location'] = iri_to_uri("%s") % request.GET.get('next')
        return result

admin.site.register(Course, CourseAdmin)
admin.site.register(CourseAttempt, CourseAttemptAdmin)
admin.site.register(Question, QuestionAdmin)
