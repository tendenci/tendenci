import traceback
from datetime import date, datetime
import time

from django.core.management.base import BaseCommand
from django.conf import settings
import requests

RATE_LIMIT = 30


class Command(BaseCommand):
    """
    Import BV exams data for the specified user or all active members.
    
    Usage: python manage.py import_bluevolt_exams_for_user --user_id 1
    
    """
    def add_arguments(self, parser):
        parser.add_argument('--user_id',
            dest='user_id',
            default=None,
            help='user_id - specify user_id')

    def go_to_sleep(self, limit_count):
        if limit_count >= RATE_LIMIT:
            time.sleep(60)
            return True
        return False

    def import_bv_exams_for_user(self, user_id=None):
        import dateutil.parser as dparser
        from tendenci.apps.profiles.models import Profile
        from tendenci.apps.trainings.models import Course, Transcript, Exam, Certification
        if not hasattr(settings, 'BLUEVOLT_API_KEY'):
            print('Bluevolt API is not set up. Exiting...')
            return 
        api_key = settings.BLUEVOLT_API_KEY
        api_endpoint_base_url = settings.BLUEVOLT_API_ENDPOINT_BASE_URL

        enrollment_url = api_endpoint_base_url + '/devapi4/api/EnrollmentsForUser'

        date_from = date(2025, 1, 1)
        date_to = date.today()

        if not user_id:
            profiles = Profile.objects.all()
        else:
            profiles = Profile.objects.filter(user__id=user_id)
        # active members only
        profiles = profiles.exclude(user__is_active=False)
        profiles = profiles.exclude(member_number='')
        profiles = profiles.exclude(external_id__isnull=True)

        if profiles.count() == 0:
            print('0 active members... exiting')
            return

        # default certification_track
        [certification_track] = Certification.objects.filter(enable_diamond=True)[:1] or [None]
        limit_count = 0 # for rate limit (30/minute)
        
        # STEP 1: Get a list of enrollments - pull the Completed only
        for profile in profiles:
            print('Processing for user ', profile)
            num_inserted = 0
            user = profile.user
            bv_user_id = profile.external_id
            headers = {'ocp-apim-subscription-key': settings.BLUEVOLT_PRIMARY_KEY}
            payload = {'apiKey': api_key,
                       'userId': bv_user_id,
                       'enrollmentStatus': 'Complete',
                       'lastUpdatedUTCStart': date_from.strftime('%Y-%m-%d'),
                       'lastUpdatedUTCEnd': date_to.strftime('%Y-%m-%d')}
            if self.go_to_sleep(limit_count):
                limit_count = 0
            r = requests.get(enrollment_url, headers=headers, params=payload)
            limit_count += 1
            if r.status_code == 200:
                enrollment_results = r.json()
                total_records = len(enrollment_results)
                print('total=', total_records)
                
                for enrollment_result in enrollment_results:
                    course_id = enrollment_result['CourseId']
                    completion_date = enrollment_result['CompletionDate']
                    if not completion_date:
                        print(f'CourseId {course_id} no complete date')
                        continue
                    if dparser.parse(completion_date) < datetime(2025, 1, 1, 0, 0, 0):
                        print('completion_date not current')
                        continue
                    
                    # STEP 2: Get course by external_id
                    course = Course.objects.filter(external_id=course_id).first()
                    if not course:
                        print(f'CourseId {course_id} not exist on site')
                        continue      
    
                    # STEP 3: Insert into transcripts if not already in there
                    #         and user has completed the course          
    
                    # check if already exists, but would someone take same courses again?
                    [transcript] = Transcript.objects.filter(course=course,
                                                             user=user,
                                                             location_type='online')[:1] or [None]
                    if not transcript:
                        
                        exam = Exam(user=user,
                                    course=course,
                                    grade=100)
                        exam.date = dparser.parse(completion_date)
                        exam.save()
                        transcript = Transcript(
                                     exam=exam,
                                     parent_id=exam.id,
                                     location_type='online',
                                     user=user,
                                     course=course,
                                     school_category=course.school_category,
                                     credits=course.credits,
                                     certification_track=certification_track,
                                     status='approved'
                                    )
                        transcript.save()
                        num_inserted += 1
                        print(transcript, f'{transcript.id}... added')
    
      
                print('num_inserted=', num_inserted)
    
                           
            else:
                print(f'ERROR: Got {r.text}')
        print('Done!')             

    def handle(self, *args, **options):
        user_id = options.get('user_id', None)
        try:
            self.import_bv_exams_for_user(user_id=user_id)
        except:
            print(traceback.format_exc())

        