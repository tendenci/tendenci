from django.utils.log import AdminEmailHandler

class CustomAdminEmailHandler(AdminEmailHandler):
    def format_subject(self, subject):
        subject = subject.split('\n')[0]
        return super().format_subject(subject)
