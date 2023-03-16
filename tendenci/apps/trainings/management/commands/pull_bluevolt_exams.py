from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings
import requests


class Command(BaseCommand):
    """
    Pull BV exams (enrollment) data through BV API.
    
    Usage: python manage.py pull_bluevolt_exams --import_id 1
    
    """
    
    def add_arguments(self, parser):
        parser.add_argument('--import_id',
            dest='import_id',
            default=None,
            help='import_id - specify import id')

    def handle(self, *args, **options):
        from datetime import datetime, date, timedelta
        from tendenci.apps.trainings.models import BluevoltExamImport, Course, Transcript, Exam, Certification
        if not hasattr(settings, 'BLUEVOLT_API_KEY'):
            print('Bluevolt API is not set up. Exiting...')
            return 
        api_key = settings.BLUEVOLT_API_KEY
        api_endpoint_base_url = settings.BLUEVOLT_API_ENDPOINT_BASE_URL
        enrollment_url = api_endpoint_base_url + 'GetUserCourseEnrollment'
        course_url = api_endpoint_base_url + 'GetCourse'
        user_url = api_endpoint_base_url + 'GetUser'
        messages = []
        num_inserted = 0

        import_id = options.get('import_id', None)
        if not import_id:
            date_from = date.today() - timedelta(days=8)
            date_to = date.today()
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
        
        # STEP 1: Get a list of enrollments
        payload = {'apiKey': api_key ,
                   'startDate': date_from.strftime('%Y-%m-%d') ,
                   'endDate': date_to.strftime('%Y-%m-%d'),
                   'enrollmentStatus': 'Complete'}
        r = requests.get(enrollment_url, params=payload)
        if r.status_code == 200:
            enrollment_results = r.json()
            messages.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' - STARTED')
            for enrollment_result in enrollment_results:
                course_id = enrollment_result['CourseId']
                user_id = enrollment_result['UserId']
                score = enrollment_result['Score']
                completion_date = enrollment_result['CompletionDate']
                # default certification_track
                [certification_track] = Certification.objects.filter(enable_diamond=True)[:1] or [None]
                
                # STEP 2: Get course detail to course code
                #TODO: Store the maps for CourseId and UserId so that we
                #    don't have to retrieve the same courses and users
                course_payload = {'apiKey': api_key,
                                  'courseId': course_id}
                course_r = requests.get(course_url, params=course_payload)
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
                    user_r = requests.get(user_url, params=user_payload)
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

                        # check if already exists
                        [transcript] = Transcript.objects.filter(course=course, user=user)[:1] or [None]
                        if not transcript:
                            transcript = Transcript(
                                         user=user,
                                         course=course,
                                         school_category=course.school_category,
                                         credits=course.credits,
                                         certification_track=certification_track,
                                         status='approved'
                                        )
                            transcript.save()
                            num_inserted += 1
                            print(transcript, '... added')
                            messages.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + f' - Transaction for Customer "{user.get_full_name()}" and Course "{course.name}" added')
                        else:
                            messages.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + f' - DUBLICATE TRANSACTION: Transaction for Customer "{user.get_full_name()}" and Course "{course.name}" already exists')
                        if score and not transcript.exam: # Question: if score is null, does it mean course has not been completed yet?
                            score = '%.0f' % float(score)
                            exam = Exam(user=user,
                                        course=course,
                                        grade=score)
                            exam.save()
                            transcript.exam = exam
                            transcript.parent_id = exam.id
                            transcript.location_type = 'online'
                            transcript.save(assign_diamond_number=False)

            end_dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if num_inserted == 1:
                messages.append(end_dt + f' - INSERTED: {num_inserted} record')
            else:
                messages.append(end_dt + f' - INSERTED: {num_inserted} records')

            messages.append(end_dt + ' - ENDED')

            if import_id and bv_import:
                # Update bv_import object
                bv_import.num_inserted = num_inserted
                bv_import.result_detail = '\n'.join(messages)
                bv_import.status_detail = 'Finished'
                bv_import.run_finish_date = datetime.now()
                bv_import.save()
                       
        else:
            print(f'ERROR: Got {r.status_code} from API')              

                
                
                                  
                
                
            
        