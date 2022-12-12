from django.contrib.auth.models import User

from tendenci.apps.trainings.models import Transcript, OutsideSchool, TeachingActivity

def user_transcripts(user, location_type='online',
                     online_courses=None,
                     onsite_courses=None):
    if isinstance(user, User):
        if location_type in ['online', 'onsite']:
            if not any([online_courses, onsite_courses]):
                return None
            transcripts = Transcript.objects.filter(
                    location_type=location_type,
                    user=user)
            if location_type == 'online' and online_courses:
                transcripts = transcripts.filter(course_id__in=online_courses)
            if location_type == 'onsite' and onsite_courses:
                transcripts = transcripts.filter(course_id__in=onsite_courses)

            return transcripts
    return None


def user_outside_schools(user):       
    if isinstance(user, User):
        return OutsideSchool.objects.filter(user=user) 
 
    return None


def user_teaching_activities(user):       
    if isinstance(user, User):
        return TeachingActivity.objects.filter(user=user) 
 
    return None      