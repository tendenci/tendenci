import requests

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Populate BV courseID to the external_id field of course table.
    
    Usage: python manage.py populate_bluevolt_courseid
    
    """
    def handle(self, *args, **options):
        from tendenci.apps.trainings.models import Course
        if not hasattr(settings, 'BLUEVOLT_API_KEY'):
            print('Bluevolt API is not set up. Exiting...')
            return 
        api_key = settings.BLUEVOLT_API_KEY
        api_endpoint_base_url = settings.BLUEVOLT_API_ENDPOINT_BASE_URL
        courses_url = api_endpoint_base_url + '/devapi2/webapi/v2/GetAllCourses'
        headers = {'ocp-apim-subscription-key': settings.BLUEVOLT_PRIMARY_KEY}
        payload = {'apiKey': api_key ,
                   'onlyActiveCourses': 'True'}
        r = requests.get(courses_url, headers=headers, params=payload)
        if r.status_code == 200:
            courses_results = r.json()
            total_records = len(courses_results)
            print('total=', total_records)
            for course_result in courses_results:
                course_code = course_result['ExternalCourseCode']
                external_id = course_result['ID']
                if Course.objects.filter(course_code=course_code,
                                         external_id=external_id).exists():
                    print(f'external_id "{external_id}" already populated.')
                    continue
                [course] = Course.objects.filter(course_code=course_code)[:1] or [None]
                if course:
                    course.external_id = external_id
                    course.save(update_fields=['external_id'])
                    print(external_id)
                else:
                    print(f'course with course code "{course_code}" does not exist.')
                