from datetime import datetime, timedelta

from courses.models import CourseAttempt

def can_retry(course, user):
    """
    Check if the user has taken this course before.
    If it is a retake, check if the current time and number of attempts
    allows her to retake the course.
    This will return a tuple where the first value is a boolean stating if
    the user can retry or not. The 2nd is a date where the user may be able to retry.
    The 2nd will be None if the user has exhausted all his/her retries.
    """
    attempts = CourseAttempt.objects.filter(course=course, user=user).order_by("-create_dt")
    if attempts:
        if course.retries == 0 or attempts.count() <= course.retries:
            #return the next possible retry time
            last_try = attempts[0].create_dt
            interval = timedelta(hours=course.retry_interval)
            next_try = last_try + interval
            if datetime.now() < next_try:
                return (False, next_try)
        else:
            #user has used up all her retries
            return (False, None)
    return (True, datetime.now())

def get_passed_attempts(course, user):
    """
    Returns the passing attempts of a user for a given course.
    """
    passed_attempts = CourseAttempt.objects.filter(
        course=course,
        user=user,
        score__gte=course.passing_score
    )
    return passed_attempts

def get_best_passed_attempt(course, user):
    """
    Returns the highest scoring attempt out of all the passing attempts
    """
    attempts = get_passed_attempts(course, user)
    if attempts:
        best = attempts.order_by('-score')[0]
        return best
    return None
