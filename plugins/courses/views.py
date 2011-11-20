from datetime import datetime, timedelta

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms.models import inlineformset_factory

from base.http import Http403
from perms.utils import get_notice_recipients, has_perm, update_perms_and_save
from perms.utils import is_admin
from event_logs.models import EventLog

from courses.models import Course, Question, CourseAttempt
from courses.forms import CourseForm, QuestionForm, AnswerForm
from courses.utils import can_retry, get_passed_attempts

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
    courses = Course.objects.search(query, user=request.user)
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


def detail(request, pk, template_name="courses/detail.html"):
    """
    Course detail view
    """
    
    course = get_object_or_404(Course, pk=pk)
    
    if has_perm(request.user, 'course.view_course', course):
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
        attempts = CourseAttempt.objects.filter(user=request.user, course=course)
        if attempts:
            return redirect('courses.completion', course.pk)
        
        return render_to_response(template_name, {'course': course}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
        
    
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
            
            messages.add_message(request, messages.INFO, 'Successfully created %s' % course)
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
        form = form_class(request.POST, instace=course, user=request.user)
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
            
            messages.add_message(request, messages.INFO, 'Successfully updated %s' % course)
            return redirect('courses.edit_questions', course.pk)
    else:
        form = form_class(instance=course, user=request.user)
       
    return render_to_response(template_name, {
        'form':form,
        'course': course,
    }, context_instance=RequestContext(request))

@login_required
def edit_questions(request, pk, template_name="courses/edit_questions.html"):
    """
    Generate a formset for questions.
    """
    
    course = get_object_or_404(Course, pk=pk)
    
    if not has_perm(request.user, 'courses.change_course', course):
        raise Http403
    
    form_class = inlineformset_factory(Course, Question, form=QuestionForm, extra=1)
    
    if request.method == "POST":
        form = form_class(request.POST, instance=course)
        if form.is_valid():
            questions = form.save(commit=False)
            for question in questions:
                question.save()
            messages.add_message(request, messages.INFO, 'Successfully updated questions for %s' % course)
            return redirect('courses.detail', course.pk)
    else:
        form = form_class(instance=course)
       
    return render_to_response(template_name, {
        'form':form,
        'course':course,
        }, context_instance=RequestContext(request))
        
@login_required
def delete(request, pk, template_name="courses/delete.html"):
    course = get_object_or_404(Course, pk=pk)
    
    if not has_perm(request.user, 'courses.delete_course', course):
        raise Http403
        
    if request.method == "POST":
        course.delete()
        messages.add_message(request, messages.INFO, 'Successfully deleted %s' % course)
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
    
    #check if user can retake/take the course
    if not can_retry(course, request.user):
        messages.add_message(request, messages.ERROR, 'You are currently not allowed to retake this course')
        return redirect('courses.detail', course.pk)
    
    forms = []
    if request.method == "POST":
        #collect all the points from each form
        points = 0
        for question in course.questions.all():
            form = AnswerForm(request.POST, question=question, prefix=question.pk)
            points = points + form.points()
        score = points * 100/course.total_points
        attempt = CourseAttempt.objects.create(user=request.user, course=course, score=score)
        return redirect('courses.completion', course.pk)
    else:
        #create a form for each question
        for question in course.questions.all():
            form = AnswerForm(question=question, prefix=question.pk)
            forms.append(form)
            
    return render_to_response(template_name, {
        'forms':forms,
        'course':course,
        }, context_instance=RequestContext(request))

def completion(request, pk, template_name="courses/completion.html"):
    """
    Generate a summary of user's course attempts
    """
    course = get_object_or_404(Course, pk=pk)
    
    if not has_perm(request.user, 'courses.view_course', course):
        raise Http403
    
    attempts = CourseAttempt.objects.filter(course=course, user=request.user).order_by("-create_dt")
    passed = get_passed_attempts(course, request.user)
    retry = can_retry(course, request.user)
    
    if isinstance(retry, timedelta):
        retry_time_left = retry
    else:
        retry_time_left = None
    
    print retry
        
    return render_to_response(template_name, {
        'attempts':attempts,
        'course':course,
        'has_passed':passed,
        'can_retry':retry,
        'retry_time_left':retry_time_left,
        }, context_instance=RequestContext(request))

def certificate(request, pk, template_name="courses/certificate.html"):
    course = get_object_or_404(Course, pk=pk)
    
    if not has_perm(request.user, 'courses.view_course', course):
        raise Http403
    
    attempt = get_best_attempt(course, request.user)
    
    if not (attempt.score >= course.passing_score):
        # there is no certificate if the user hasn't passed the course yet
        raise Http404
    
    return render_to_response(template_name, {
        'course':course,
        'attempt':attempt,
        }, context_instance=RequestContext(request))
