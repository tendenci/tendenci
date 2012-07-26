from django.contrib import admin
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.conf import settings

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.courses.models import Course, Question, Answer, CourseAttempt
from tendenci.apps.courses.forms import CourseForm, QuestionForm, QuestionFormset

class CourseAttemptAdmin(admin.ModelAdmin):
    list_display = ['course', 'user', 'score', 'create_dt']
    
class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 2
    
class QuestionAdmin(admin.ModelAdmin):
    inlines = [
        AnswerInline,
    ]
    
    list_display = ['question', 'course', 'view_on_site']
    ordering = ['course']
    list_filter = ['course']
    fields = ['course', 'question', 'point_value']
    
    def view_on_site(self, obj):
        link_icon = '%simages/icons/external_16x16.png' % settings.STATIC_URL
        link = '<a href="%s" title="%s"><img src="%s" /></a>' % (
            reverse('courses.questions', args=[obj.course.pk]),
            obj.course,
            link_icon,
        )
        return link
    view_on_site.allow_tags = True
    view_on_site.short_description = 'view'
    
    def response_change(self, request, obj, post_url_continue=None):
        return redirect('courses.questions', obj.pk)
    
    def response_add(self, request, obj, post_url_continue=None):
        return redirect('/admin/courses/course/%s' % obj.course.pk)

class QuestionInline(admin.TabularInline):
    model = Question
    form = QuestionForm
    formset = QuestionFormset
    extra = 0


class CourseAdmin(TendenciBaseModelAdmin):
    inlines = [
        QuestionInline,
    ]
    list_display = ['title', 'deadline', 'passing_score', 'status']
    list_filter = []
    search_fields = []
    fieldsets = (
        (None, 
            {'fields': (
                'title',
                'content',
                'recipients',
                'can_retry',
                'retries',
                'retry_interval',
                'passing_score',
                'deadline',
                'close_after_deadline',
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
    add_form_template = "courses/admin/add_form.html"

    class Media:
        js = (
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
            '%sjs/jquery-1.6.2.min.js' % settings.STATIC_URL,
            #'%sjs/jquery_ui_all_custom/jquery-ui-1.8.5.custom.min.js' % settings.STATIC_URL,
            #'https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js',
            'https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.18/jquery-ui.min.js',
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
            '%sjs/admin/courses-inline-ordering.js' % settings.STATIC_URL,
        )
        css = {'all': ['%scss/admin/dynamic-inlines-with-sort.css' % settings.STATIC_URL], }

    def response_add(self, request, obj, post_url_continue=None):
        return redirect('courses.questions', obj.pk)

    def response_change(self, request, obj, post_url_continue=None):
        return redirect('courses.questions', obj.pk)

admin.site.register(Course, CourseAdmin)
admin.site.register(CourseAttempt, CourseAttemptAdmin)
admin.site.register(Question, QuestionAdmin)
