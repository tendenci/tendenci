import traceback
from logging import getLogger
from datetime import datetime, date, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse
import requests


class Command(BaseCommand):
    """
    Import BV exams data through BV API.
    
    Per Astro Whang at BlueVolt, there is no credits field, no grade/score can be looked up to
    determine if a user has passed a course. Instead, we should utilize the enrollment status of 
    "Complete".
    Astro Whang: There is no “credit” field and instead you’ll be utilizing the enrollment 
    status of “Complete” to credit the learners who have completed the course.
    
    Usage: python manage.py import_bluevolt_exams --import_id 1
    
    """
    
    def add_arguments(self, parser):
        parser.add_argument('--import_id',
            dest='import_id',
            default=None,
            help='import_id - specify import id')

    def import_bv_exams(self, import_id=None):
        import dateutil.parser as dparser
        from tendenci.apps.trainings.models import BluevoltExamImport, Course, Transcript, Exam, Certification
        if not hasattr(settings, 'BLUEVOLT_API_KEY'):
            print('Bluevolt API is not set up. Exiting...')
            return 
        api_key = settings.BLUEVOLT_API_KEY
        api_endpoint_base_url = settings.BLUEVOLT_API_ENDPOINT_BASE_URL
        #enrollment_url = api_endpoint_base_url + 'GetUserCourseEnrollment'
        # Currently, we have to use both v2 and v3 APIs to get what we need
        #score_url = api_endpoint_base_url + '/v3/modules/scores'
        #module_url = api_endpoint_base_url + '/v2/GetModule'
        enrollment_url = api_endpoint_base_url + '/devapi3/webapi/v3/enrollments'
        course_url = api_endpoint_base_url + '/devapi2/webapi/v2/GetCourse'
        user_url = api_endpoint_base_url + '/devapi2/webapi/v2/GetUser'
        messages = []
        num_inserted = 0

        if not import_id:
            date_from = date.today() - timedelta(days=7)
            date_to = date.today()
            bv_import = BluevoltExamImport(
                                    date_from=date_from,
                                    date_to=date_to,
                                    status_detail='Running',
                                    run_start_date = datetime.now())
            bv_import.save()
        else:
            [bv_import] = BluevoltExamImport.objects.filter(id=import_id)[:1] or [None]
            if not bv_import:
                raise CommandError(f'BluevoltExamImport with id {import_id} not found!')
            
            if bv_import.status_detail == 'Pending':
                bv_import.status_detail = 'Running'
                bv_import.run_start_date = datetime.now()
                bv_import.save()
            date_from = bv_import.date_from
            date_to = bv_import.date_to

        # testing, remove later
        # --------------------
        # date_from = date.today() - timedelta(days=2)
        # date_to = date.today()
        # ----------------
        
        # STEP 1: Get a list of enrollments - pull the Completed only
        headers = {'ocp-apim-subscription-key': settings.BLUEVOLT_PRIMARY_KEY}
        payload = {'apiKey': api_key ,
                   'enrollmentStatus': 'Complete',
                   'lastUpdatedUTCStart': date_from.strftime('%Y-%m-%d') ,
                   'lastUpdatedUTCEnd': date_to.strftime('%Y-%m-%d')}
        r = requests.get(enrollment_url, headers=headers, params=payload)
        if r.status_code == 200:
            enrollment_results = r.json()
            messages.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' - STARTED')
            messages.append(f'Total: {len(enrollment_results)}')
            # default certification_track
            [certification_track] = Certification.objects.filter(enable_diamond=True)[:1] or [None]

            for enrollment_result in enrollment_results['Collection']:
                course_id = enrollment_result['CourseId']
                user_id = enrollment_result['UserId']
                completion_date = enrollment_result['CompletionDate']
                
                # STEP 2: Get course detail to course code
                #TODO: Store the maps for CourseId and UserId so that we
                #    don't have to retrieve the same courses and users
                course_payload = {'apiKey': api_key,
                                  'courseId': course_id}
                course_r = requests.get(course_url, headers=headers, params=course_payload)
                if course_r.status_code == 200:
                    course_result = course_r.json()
                    course_code = course_result['ExternalCourseCode']
                    # given course_code, find the course
                    [course] = Course.objects.filter(course_code=course_code)[:1] or [None]
                    if not course:
                        msg = f'Course with course code {course_code} does not exist!'
                        print(msg)
                        messages.append(msg)
                        continue

                    # STEP 3: Get user info to find username
                    user_payload = {'apiKey': api_key,
                                    'userID': user_id}
                    user_r = requests.get(user_url, headers=headers, params=user_payload)
                    if user_r.status_code == 200:
                        user_result = user_r.json()[0]
                        username = user_result['UserName']
                        # given a username, find the user
                        [user] = User.objects.filter(username=username)[:1] or [None]
                        if not user:
                            msg = f'User with username {username} does not exist!'
                            print(msg)
                            messages.append(msg)
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
                            #messages.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + f' - Transaction for Customer "{user.get_full_name()}" and Course "{course.name}" added')
                        #else:
                            #messages.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + f' - DUBLICATE TRANSACTION: Transaction for Customer "{user.get_full_name()}" and Course "{course.name}" already exists')

            end_dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if num_inserted == 1:
                messages.append(end_dt + f' - INSERTED: {num_inserted} record')
            else:
                messages.append(end_dt + f' - INSERTED: {num_inserted} records')

            messages.append(end_dt + ' - ENDED')

            if bv_import:
                # Update bv_import object
                bv_import.num_inserted = num_inserted
                bv_import.result_detail = '\n'.join(messages)
                bv_import.status_detail = 'Finished'
                bv_import.run_finish_date = datetime.now()
                bv_import.save()
                       
        else:
            print(f'ERROR: Got {r.status_code} from API')
        print('Done!')             

    def handle(self, *args, **options):
        from tendenci.apps.site_settings.utils import get_setting
        logger = getLogger('import_bv_exams')
        import_id = options.get('import_id', None)
        try:
            self.import_bv_exams(import_id=import_id)
        except:
            print(traceback.format_exc())
            url = get_setting('site', 'global', 'siteurl')
            if import_id:
                url += reverse('admin:trainings_bluevoltexamimport_change', args=[import_id])
            
            logger.error(f'Error importing training exams from BV {url}...\n\n{traceback.format_exc()}')
        