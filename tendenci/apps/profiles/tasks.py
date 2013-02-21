from celery.task import Task
from celery.registry import tasks
from tendenci.core.imports.utils import render_excel
from tendenci.apps.profiles.models import Profile


class ExportProfilesTask(Task):

    def run(self, **kwargs):
        """
        Return a csv of all profles
        """
        filename = "profiles_export.csv"

        field_list = [
            'username',
            'first_name',
            'last_name',
            'email',
            'pl_id',
            'member_number',
            'historical_member_number',
            'time_zone',
            'language',
            'salutation',
            'initials',
            'display_name',
            'mailing_name',
            'company',
            'position_title',
            'position_assignment',
            'sex',
            'address_type',
            'address',
            'address2',
            'city',
            'state',
            'zipcode',
            'country',
            'county',
            'phone',
            'phone2',
            'fax',
            'work_phone',
            'home_phone',
            'mobile_phone',
            'email',
            'email2',
            'url',
            'url2',
            'dob',
            'ssn',
            'spouse',
            'department',
            'education',
            'student',
            'remember_login',
            'exported',
            'direct_mail',
            'notes',
            'admin_notes',
            'referral_source',
            'hide_in_search',
            'hide_address',
            'hide_email',
            'hide_phone',
            'first_responder',
            'agreed_to_tos',
            'original_username',
            '\n',
        ]

        data_rows = []
        profiles = Profile.objects.all()

        for profile in profiles:
            data_row = [
                profile.user.username,
                profile.user.first_name,
                profile.user.last_name,
                profile.user.email,
                profile.pl_id,
                profile.member_number,
                profile.historical_member_number,
                profile.time_zone,
                profile.language,
                profile.salutation,
                profile.initials,
                profile.display_name,
                profile.mailing_name,
                profile.company,
                profile.position_title,
                profile.position_assignment,
                profile.sex,
                profile.address_type,
                profile.address,
                profile.address2,
                profile.city,
                profile.state,
                profile.zipcode,
                profile.country,
                profile.county,
                profile.phone,
                profile.phone2,
                profile.fax,
                profile.work_phone,
                profile.home_phone,
                profile.mobile_phone,
                profile.email2,
                profile.url,
                profile.url2,
                profile.dob,
                profile.ssn,
                profile.spouse,
                profile.department,
                profile.education,
                profile.student,
                profile.remember_login,
                profile.exported,
                profile.direct_mail,
                profile.notes,
                profile.admin_notes,
                profile.referral_source,
                profile.hide_in_search,
                profile.hide_address,
                profile.hide_email,
                profile.hide_phone,
                profile.first_responder,
                profile.agreed_to_tos,
                profile.original_username,
                '\n',
            ]
            data_rows.append(data_row)

        return render_excel(filename, field_list, data_rows, '.csv')

tasks.register(ExportProfilesTask)
