from datetime import datetime, timedelta

from courses.models import CourseAttempt

def can_retry(course, user):
    """
    Check if the user has taken this course before.
    If it is a retake, check if the current time and number of attempts
    allows her to retake the course.
    If she/he cannot retry, return the time interval for the next retry.
    """
    attempts = CourseAttempt.objects.filter(course=course, user=user).order_by("-create_dt")
    if attempts:
        if course.retries == 0 or attempts.count() <= course.retries:
            #redirect if the user is not yet allowed to retake the course
            last_try = datetime.now() - attempts[0].create_dt
            interval = timedelta(hours=course.retry_interval)
            if last_try < interval:
                return interval - last_try
        else:
            #user has used up all her retries
            return False
    return True

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
