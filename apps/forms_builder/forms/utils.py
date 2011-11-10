import re
from os.path import basename
from django.conf import settings
from django.template import Context
from django.template.loader import get_template
from site_settings.utils import get_setting

def generate_email_body(entry):
    """
        Generates the email body so that is readable
    """
    context = Context()
    site_url = get_setting('site', 'global', 'siteurl')
    if site_url[-1:] == "/":
        site_url = site_url[:-1]
    print site_url
    template = get_template('forms/email_content.html')
    
    # fields to loop through in the template
    context['fields'] = entry.fields.all()
    # media_url necessary for file upload fields
    context['media_url'] = site_url + settings.MEDIA_URL
    # title to show in the email
    context['title'] = entry.form.title
    output = template.render(context)

    return output

def generate_email_subject(form, form_entry):
    """
        Generates email subject from subject template
    """
    if form.subject_template:
        subject = form.subject_template
        field_entries = form_entry.fields.all()
        for field_entry in field_entries:
            label = field_entry.field.label
            value = field_entry.value
            # removes parens so they don't break the re compile.
            label = re.sub('[()]', '', label)
            if not value:
                value = ''
                p = re.compile('(-\s+)?\[%s\]' % label, re.IGNORECASE)
            else:
                p = re.compile('\[%s\]' % label, re.IGNORECASE)
            subject = p.sub(value, subject)
            
        # title
        p = re.compile('\[title\]', re.IGNORECASE)
        subject = p.sub(form.title, subject)
            
        # replace those brackets with blank string
        p = re.compile('(-\s+)?\[[\d\D\s\S\w\W]*?\]')
        subject = p.sub('', subject)
    
    else:
        subject = "%s:" % (form.title)
        if form_entry.get_first_name():
            subject = "%s %s" % (subject, form_entry.get_first_name())
        if form_entry.get_last_name():
            subject = "%s %s" % (subject, form_entry.get_last_name())
        if form_entry.get_full_name():
            subject = "%s %s" % (subject, form_entry.get_full_name())
        if form_entry.get_phone_number():
            subject = "%s - %s" % (subject, form_entry.get_phone_number())
        if form_entry.get_email_address():
            subject = "%s - %s" % (subject, form_entry.get_email_address())
        
    return subject
    
    
