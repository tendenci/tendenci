import calendar
from decimal import Decimal
from datetime import datetime, timedelta

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic

from perms.object_perms import ObjectPermission
from tagging.fields import TagField

from perms.models import TendenciBaseModel
from courses.managers import CourseManager

class Course(TendenciBaseModel):
    """
    Courses plugin base model.
    You can think of this as test since there will be several questions
    linked to it.
    """
    
    title = models.CharField(_(u'Title'), max_length=200)
    content = models.TextField(_(u'Content'))
    retries = models.IntegerField(_(u'Retries'), help_text=u'Number of retries allowed (0, means unlimited)', default=0)
    retry_interval = models.IntegerField(_(u'Retry Interval'), help_text=u'Number of hours before another retry', default=0)
    passing_score = models.DecimalField(_(u'Passing Score'),
                        help_text=u'out of 100%',
                        max_digits=5,
                        decimal_places=2,
                        validators=[MaxValueValidator(Decimal('100')), MinValueValidator(Decimal('0'))],
                    )
    deadline = models.DateTimeField(_(u'Deadline'), null=True)
    close_after_deadline = models.BooleanField(_(u'Close After Deadline'), default=False)
    tags = TagField(blank=True, help_text='Tag 1, Tag 2, ...')
    
    perms = generic.GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")
    
    objects = CourseManager()
    
    class Meta:
        permissions = (("view_course","Can view course"),)
    
    def __unicode__(self):
        return self.title
    
    @models.permalink
    def get_absolute_url(self):
        return ("courses.detail", [self.pk])
    
    @property
    def total_points(self):
        total_points = 0
        for question in self.questions.all():
            total_points = total_points + question.point_value
        return total_points
    
    def is_closed(self):
        return (self.close_after_deadline and self.deadline_has_passed())
        
    def deadline_has_passed(self):
        if self.deadline:
            return (datetime.now() > self.deadline)
        return False
        
    def user_attempts(self):
        d = {}
        attempts = self.attempts.all()
        for a in attempts:
            if a.user in d.keys():
                d[a.user]['list'].append(a)
            else:
                d[a.user] = {}
                d[a.user]['user'] = a.user
                d[a.user]['list'] = [a,]
        
        l = []
        for u in d.keys():
            l.append(d[u])
        return l
            

class Question(models.Model):
    """Represents a single question for a course.
    point_value should always be equal to 100 over total number of course questions.
    """
    course = models.ForeignKey(Course, related_name="questions")
    number = models.IntegerField(_(u'Number'))
    question = models.CharField(_(u'Question'), max_length=200)
    point_value = models.IntegerField(_(u'Point Value'), default=0)
    
    def __unicode__(self):
        return "%s: %s" % (self.course.title, self.question)
        
    def correct_answers(self):
        return self.answers.filter(correct=True)
        
    def choices(self):
        cl = []
        letters = map(chr, range(97, 123))
        answers = self.answers.all()
        for i in range(min([len(letters)], len(answers))):
            cl.append({
                'letter':letters[i],
                'answer':answers[i]
            })
        return cl
        
class Answer(models.Model):
    """Represents an Answer choice for a question.
    """
    question = models.ForeignKey(Question, related_name="answers")
    answer = models.CharField(_(u'answer'), max_length=100)
    correct = models.BooleanField(_(u'is correct'))
    
    def __unicode__(self):
        return "%s: %s" % (self.question.question, self.answer)

class CourseAttempt(models.Model):
    """
    Represents course attempts.
    We can also use this to represent course completions and failures.
    """
    course = models.ForeignKey(Course, related_name="attempts")
    user = models.ForeignKey(User)
    score =  models.DecimalField(_(u'Score'), help_text=_(u'out of 100%'), max_digits=5, decimal_places=2)
    create_dt = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(_(u'Notes'), blank=True, default=u'')
    
    def __unicode__(self):
        return "%s" % (self.course.title)
    
    @property
    def passed(self):
        if self.score >= self.course.passing_score:
            return True
        return False
