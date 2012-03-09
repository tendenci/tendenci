from datetime import datetime, timedelta

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory

from base.http import Http403
from perms.utils import get_notice_recipients, has_perm, update_perms_and_save
from perms.utils import is_admin, get_query_filters
from event_logs.models import EventLog
from site_settings.utils import get_setting

from courses.models import Course, Question, CourseAttempt
from courses.forms import (CourseForm, QuestionForm, AnswerForm,
    CourseAttemptForm, DateRangeForm)
from courses.utils import (can_retry, get_passed_attempts, get_top_tests,
    get_best_passed_attempt)

try:
    from notification import models as notification
except:
    notification = None

def index(request, template_name="courses/detail.html"):
    return redirect('courses.search')


def search(request, template_name="courses/search.html"):
    """
    Search view for courses
    """
    
    query = request.GET.get('q', None)
    if get_setting('site', 'global', 'searchindex') and query:
        courses = Course.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'courses.view_course')
        courses = Course.objects.filter(filters).distinct()
        if request.user.is_authenticated():
            courses = courses.select_related()

    courses = courses.order_by('-create_dt')

    log_defaults = {
        'event_id' : 113400,
        'event_data': '%s searched by %s' % ('Course', request.user),
        'description': '%s searched' % 'Course',
        'user': request.user,
        'request': request,
        'source': 'courses'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'courses':courses}, 
        context_instance=RequestContext(request))

@login_required
def detail(request, pk, template_name="courses/detail.html"):
    """
    Course detail view
    """
    course = get_object_or_404(Course, pk=pk)
    
    if not has_perm(request.user, 'course.view_course', course):
        raise Http403
        
    log_defaults = {
        'event_id' : 113500,
        'event_data': '%s (%d) viewed by %s' % (course._meta.object_name, course.pk, request.user),
        'description': '%s viewed' % course._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': course,
    }
    EventLog.objects.log(**log_defaults)
    
    #check if the user has attempted this course before
    attempted = CourseAttempt.objects.filter(user=request.user, course=course).exists()
    passed = get_passed_attempts(course, request.user)
    retry, retry_time = can_retry(course, request.user)
    
    return render_to_response(template_name, {
        'course':course,
        'attempted':attempted,
        'has_passed':passed,
        'can_retry':retry,
        'retry_time_left':retry_time,
    }, context_instance=RequestContext(request))
        
@login_required
def add(request, form_class=CourseForm, template_name="courses/add.html"):
    """
    Add a course then redirect to the question creation page for the course.
    """
    
    if not has_perm(request.user, 'courses.add_course'):
        raise Http403
        
    if request.method == "POST":
        form = form_class(request.POST, user=request.user)
        if form.is_valid():
            course = form.save(commit=False)
            
            # add all permissions and save the model
            course = update_perms_and_save(request, form, course)
            
            log_defaults = {
                'event_id' : 113000,
                'event_data': '%s (%d) added by %s' % (course._meta.object_name, course.pk, request.user),
                'description': '%s added' % course._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': course,
            }
            EventLog.objects.log(**log_defaults)
            
            messages.add_message(request, messages.SUCCESS, 'Successfully created %s' % course)
            return redirect('courses.edit_questions', course.pk)
    else:
        form = form_class(user=request.user)
       
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))
        
@login_required
def edit(request, pk, form_class=CourseForm, template_name="courses/edit.html"):
    """
    Add a course then redirect to the question creation page for the course.
    """
    
    course = get_object_or_404(Course, pk=pk)
    
    if not has_perm(request.user, 'courses.change_course', course):
        raise Http403
        
    if request.method == "POST":
        form = form_class(request.POST, instance=course, user=request.user)
        if form.is_valid():
            course = form.save(commit=False)
            
            # add all permissions and save the model
            course = update_perms_and_save(request, form, course)
            
            log_defaults = {
                'event_id' : 113000,
                'event_data': '%s (%d) added by %s' % (course._meta.object_name, course.pk, request.user),
                'description': '%s added' % course._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': course,
            }
            EventLog.objects.log(**log_defaults)
            
            messages.add_message(request, messages.SUCCESS, 'Successfully updated %s' % course)
            return redirect('courses.edit_questions', course.pk)
    else:
        form = form_class(instance=course, user=request.user)
       
    return render_to_response(template_name, {
        'form':form,
        'course': course,
    }, context_instance=RequestContext(request))
    
@login_required
def questions(request, pk, template_name="courses/questions.html"):
    """List all the questions of a course
    """
    
    course = get_object_or_404(Course, pk=pk)
    
    if not has_perm(request.user, 'courses.change_course', course):
        raise Http403
        
    return render_to_response(template_name, {
        'course':course,
        'questions':course.questions.all(),
    }, context_instance=RequestContext(request))


@login_required
def delete(request, pk, template_name="courses/delete.html"):
    course = get_object_or_404(Course, pk=pk)
    
    if not has_perm(request.user, 'courses.delete_course', course):
        raise Http403
        
    if request.method == "POST":
        course.delete()
        messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % course)
        return redirect("courses.search")
    
    return render_to_response(template_name, {
        'course':course,
        }, context_instance=RequestContext(request))

        
@login_required
def take(request, pk, template_name="courses/take.html"):
    """
    User takes the course. Present the user with the course's list of questions
    Create a CourseAttempt entry when the user submits his/her answers.
    """
    course = get_object_or_404(Course, pk=pk)
    
    if not has_perm(request.user, 'course.view_course', course):
        raise Http403
    
    # closed course, deadline passed
    if course.is_closed() and not is_admin(request.user):
        raise Http403
    
    #check if user can retake/take the course
    if not can_retry(course, request.user):
        messages.add_message(request, messages.ERROR, 'You are currently not allowed to retake this course')
        return redirect('courses.detail', course.pk)
    
    #check if this course has any questions at all
    questions = course.questions.all()
    if not questions:
        messages.add_message(request, messages.ERROR, 'This course does not have any questions yet. Try again later.')
        return redirect('courses.detail', course.pk)
    
    forms = []
    if request.method == "POST":
        #collect all the points from each form
        points = 0
        for question in questions:
            form = AnswerForm(request.POST, question=question, prefix=question.pk)
            points = points + form.points()
        score = points * 100/course.total_points
        attempt = CourseAttempt.objects.create(user=request.user, course=course, score=score)
        
        # send notification to course taker
        recipients = [request.user.email]
        if recipients:
            if notification:
                passed = get_passed_attempts(course, request.user)
                retry, retry_time = can_retry(course, request.user)
                extra_context = {
                    'attempt':attempt,
                    'has_passed':passed,
                    'can_retry':retry,
                    'retry_time_left':retry_time,
                    'SITE_GLOBAL_SITEDISPLAYNAME': get_setting('site', 'global', 'sitedisplayname'),
                    'SITE_GLOBAL_SITEURL': get_setting('site', 'global', 'siteurl'),
                }
                notification.send_emails(recipients, 'course_completion', extra_context)
                
        # send notification to administrators
        recipients = get_notice_recipients('module', 'courses', 'courserecipients')
        if recipients:
            if notification:
                attempt_count = CourseAttempt.objects.filter(user=request.user, course=course).count()
                extra_context = {
                    'for_admin':True,
                    'attempt_count':attempt_count,
                    'attempt':attempt,
                    'has_passed':passed,
                    'can_retry':retry,
                    'retry_time_left':retry_time,
                    'SITE_GLOBAL_SITEDISPLAYNAME': get_setting('site', 'global', 'sitedisplayname'),
                    'SITE_GLOBAL_SITEURL': get_setting('site', 'global', 'siteurl'),
                }
                notification.send_emails(recipients, 'course_completion', extra_context)
        
        return redirect('courses.completion', course.pk)
    else:
        #create a form for each question
        for question in questions:
            form = AnswerForm(question=question, prefix=question.pk)
            forms.append(form)
            
    return render_to_response(template_name, {
        'forms':forms,
        'course':course,
        }, context_instance=RequestContext(request))

@login_required
def completion(request, pk, user_id=None, template_name="courses/completion.html"):
    """
    Generate a summary of user's course attempts
    """
    course = get_object_or_404(Course, pk=pk)
    
    if not has_perm(request.user, 'courses.view_course', course):
        raise Http403
        
    if user_id and is_admin(request.user):
        # allow an admin user to view other certificates
        user = User.objects.get(id=user_id)
        for_admin = True
    else:
        user = request.user
        for_admin = False
    
    attempts = CourseAttempt.objects.filter(course=course, user=user).order_by("-create_dt")
    
    passed = get_passed_attempts(course, user)
    retry, retry_time = can_retry(course, user)
        
    return render_to_response(template_name, {
        'for_admin':for_admin,
        'attempts':attempts,
        'course':course,
        'has_passed':passed,
        'can_retry':retry,
        'retry_time_left':retry_time,
        }, context_instance=RequestContext(request))

@login_required
def certificate(request, pk, template_name="courses/certificate.html"):
    course = get_object_or_404(Course, pk=pk)
    
    if not has_perm(request.user, 'courses.view_course', course):
        raise Http403
    
    attempt = get_best_passed_attempt(course, request.user)
    
    if not attempt:
        # there is no certificate if the user hasn't passed the course yet
        raise Http404
    
    return render_to_response(template_name, {
        'course':course,
        'attempt':attempt,
        }, context_instance=RequestContext(request))

@login_required
def add_completion(request, pk, template_name="courses/add_completion.html"):
    """
    Completion add for admin only
    """
    course = get_object_or_404(Course, pk=pk)
    
    if not is_admin(request.user):
        raise Http403
    
    if request.method == "POST":
        form = CourseAttemptForm(request.POST)
        if form.is_valid():
            attempt = form.save()
            return redirect('courses.completion_report', attempt.course.pk)
    else:
        form = CourseAttemptForm()
        
    return render_to_response(template_name, {
        'course':course,
        'form':form,
        }, context_instance=RequestContext(request))
        
@login_required
def clone(request, pk, form_class=CourseForm, template_name="courses/add.html"):
    """
    Add a course with a chosen course's details then
    redirect to the question creation page for the new course.
    Admin only.
    """
    
    course = get_object_or_404(Course, pk=pk)
    
    if not is_admin(request.user):
        raise Http403
        
    if request.method == "POST":
        form = form_class(request.POST, user=request.user)
        if form.is_valid():
            clone = form.save(commit=False)
            
            # add all permissions and save the model
            clone = update_perms_and_save(request, form, clone)
            
            #copy all related questions of the original
            for question in course.questions.all():
                Question.objects.create(
                        course=clone,
                        question=question.question,
                        answer=question.answer,
                        answer_choices=question.answer_choices,
                        point_value=question.point_value,
                    )
            
            log_defaults = {
                'event_id' : 113000,
                'event_data': '%s (%d) added by %s' % (course._meta.object_name, course.pk, request.user),
                'description': '%s added' % course._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': course,
            }
            EventLog.objects.log(**log_defaults)
            
            messages.add_message(request, messages.SUCCESS, 'Successfully created %s' % clone)
            return redirect('courses.edit_questions', clone.pk)
    else:
        form = form_class(instance=course, user=request.user)
       
    return render_to_response(template_name,{
        'form':form
        },context_instance=RequestContext(request))

@login_required
def completion_report(request, pk, template_name="courses/completion_report.html"):
    """
    Admin report view for listing all the CourseAttempts for a Course
    """
    course = get_object_or_404(Course, pk=pk)
    
    if not is_admin(request.user):
        raise Http403
    
    # get the date range
    form = DateRangeForm(request.GET)
    if form.is_valid():
        start_dt = form.cleaned_data['start_dt']
        end_dt = form.cleaned_data['end_dt']
    else:
        #default to 30 days ago
        form = DateRangeForm()
        start_dt = datetime.now() - timedelta(days=30)
        end_dt = datetime.now()
    
    p_attempts = CourseAttempt.objects.filter(course=course, score__gte=course.passing_score)
    f_attempts = CourseAttempt.objects.filter(course=course, score__lt=course.passing_score)
    
    if start_dt:
        p_attempts = p_attempts.filter(create_dt__gte=start_dt)
        f_attempts = f_attempts.filter(create_dt__gte=start_dt)
    
    if end_dt:
        p_attempts = p_attempts.filter(create_dt__lte=end_dt)
        f_attempts = f_attempts.filter(create_dt__lte=end_dt)
    
    return render_to_response(template_name, {
        'course':course,
        'p_attempts':p_attempts,
        'f_attempts':f_attempts,
        'form':form,
        }, context_instance=RequestContext(request))

@login_required
def top_tests(request, template_name="courses/top_tests.html"):
    """
    Admin report view for course rankings and statistics
    """
    if not is_admin(request.user):
        raise http403
    
    # get the date range
    form = DateRangeForm(request.GET)
    if form.is_valid():
        start_dt = form.cleaned_data['start_dt']
        end_dt = form.cleaned_data['end_dt']
    else:
        #default to 30 days ago
        form = DateRangeForm()
        start_dt = datetime.now() - timedelta(days=30)
        end_dt = datetime.now()
    
    courses = get_top_tests(start_dt, end_dt)
    
    return render_to_response(template_name, {
        'courses':courses,
        'form':form,
        }, context_instance=RequestContext(request))
    
