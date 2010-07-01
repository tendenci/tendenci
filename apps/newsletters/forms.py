import datetime
from django import forms
from actions.models import Action
from django.forms.extras.widgets import SelectDateWidget
from django.utils.translation import ugettext_lazy as _

THIS_YEAR = datetime.date.today().year
DAYS_CHOICES = ((1,'1'), (3,'3'), (5,'5'), (7,'7'),
                (14,'14'), (30,'30'), (60,'60'), (90,'90'),
                (120,'120'), (0,'ALL'),
                )
INCLUDE_CHOICES = ((1, 'Include'),(0, 'Skip'),)

class NewsletterAddForm(forms.ModelForm):
    subject = forms.CharField(max_length=250, error_messages={'required': 'Please enter the subject.'},
                              widget=forms.TextInput(attrs={'size':'60',
                                                            'class': 'newsletter-subject'}))
    personalize_subject_first_name = forms.BooleanField(initial=0, required=False)
    personalize_subject_last_name = forms.BooleanField(initial=0, required=False)
    include_login = forms.BooleanField(initial=0, required=False)
    jump_links = forms.ChoiceField(initial=1, choices=INCLUDE_CHOICES)
    events =  forms.ChoiceField(initial=1, choices=INCLUDE_CHOICES)
    event_start_dt = forms.DateField(required=False, widget=SelectDateWidget(None, range(THIS_YEAR, THIS_YEAR+10)))
    event_end_dt = forms.DateField(required=False, widget=SelectDateWidget(None, range(THIS_YEAR, THIS_YEAR+10)))
    articles = forms.ChoiceField(initial=1, choices=INCLUDE_CHOICES)
    articles_days = forms.ChoiceField(initial=60, choices=DAYS_CHOICES)
    news = forms.ChoiceField(initial=1, choices=INCLUDE_CHOICES)
    news_days = forms.ChoiceField(initial=30, choices=DAYS_CHOICES)
    jobs = forms.ChoiceField(initial=1, choices=INCLUDE_CHOICES)
    jobs_days = forms.ChoiceField(initial=30, choices=DAYS_CHOICES)
    pages = forms.ChoiceField(initial=0, choices=INCLUDE_CHOICES)
    pages_days = forms.ChoiceField(initial=7, choices=DAYS_CHOICES)
    template = forms.CharField(max_length=250, error_messages={'required': 'Please select a template.'})
    format = forms.CharField(widget=forms.RadioSelect(choices=((0, 'Detailed - original format'), 
                                                              (1, 'Simplified - removes AUTHOR, '+\
                                                               'POSTED BY, RELEASES DATE, etc from the detailed format'),)), 
                                                               initial=0, )
    
    class Meta:
        model = Action
        fields = ('member_only',
                  'group',
                  'send_to_email2',
                  'subject',
                  'personalize_subject_first_name',
                  'personalize_subject_last_name',
                  'include_login',
                  'jump_links',
                  'events',
                  'event_start_dt',
                  'event_end_dt',
                  'articles',
                  'articles_days',
                  'news',
                  'news_days',
                  'jobs',
                  'jobs_days',
                  'pages',
                  'pages_days',
                  'template',
                  'format',
                  )
        
    def clean(self):
        if not self.cleaned_data["member_only"] and not self.cleaned_data["group"]:
            raise forms.ValidationError(_("You must choose either a User Group or Members Only."))
        else:
            if self.cleaned_data["member_only"] and self.cleaned_data["group"]:
                raise forms.ValidationError(_("User Group and Members Only cannot both be selected."))
        return self.cleaned_data
    
    def save(self, request):
        from django.template.loader import render_to_string
        from django.template import RequestContext
        from emails.models import Email
        from newsletters.utils import newsletter_articles_list
        from site_settings.utils import get_setting
        
        # converted from function newsletters_generate_processor
        opening_text = render_to_string('newsletters/opening_text.txt', 
                                        context_instance=RequestContext(request))
        simplified = self.cleaned_data['format']
        
        # articles
        art_content = ""
        if self.cleaned_data['articles']:
            articles_days = self.cleaned_data['articles_days']
            art_content = newsletter_articles_list(request, articles_days, simplified)
            
        # calendar events    
        event_content = ""
        if self.cleaned_data['events']:
            pass
        
        # news
        news_content = ""
        if self.cleaned_data['news']:
            pass
        
        # jobs
        job_content = ""
        if self.cleaned_data['jobs']:
            pass
        
        # pages
        page_content = ""
        if self.cleaned_data['pages']:
            pass
        
        # jumplink
        jumplink_content = ""
        if self.cleaned_data['jump_links']:
            jumplink_content = render_to_string('newsletters/jumplinks.txt', locals(), 
                                        context_instance=RequestContext(request))
            
        # login block
        login_content = ""
        if self.cleaned_data['include_login']:
            login_content = render_to_string('newsletters/login.txt',  
                                        context_instance=RequestContext(request))
            
        # rss list
        
        
        email_d = {}
        email_d["[content]"] = opening_text
        
        # get the newsletter template now
        template = 'newsletters/templates/%s' % (self.cleaned_data['template'])
        email_d['template_path_name'] = template
        
        #check if we have [jumplink] in the email template, if not, 
        #include the jumplinks at the top of the newsletter
        template_content = render_to_string(template)
        if jumplink_content:
            if template_content.find("[jumplinks]") == -1:
                email_d["[content]"] += jumplink_content
                
        email_d["[content]"] += "%s%s%s%s%s%s" % (login_content, event_content, art_content,
                                news_content, job_content, page_content)
        email_d["[jumplinks]"] = jumplink_content
        email_d["[articles]"] = art_content
        email_d["[calendarevents]"] = event_content
        email_d["[events]"] = event_content
        email_d["[jobs]"] = job_content
        email_d["[contentmanagers]"] = page_content
        email_d["[pages]"] = page_content
        email_d["[releases]"] = news_content
        email_d["[news]"] = news_content
        
        email_d["[sitewebmaster]"] = get_setting('site', "global", "sitewebmaster")
        email_d["[sitedisplayname]"] = get_setting('site', "global", "sitedisplayname")
        
        today = datetime.date.today()
        email_d["[monthsubmitted]"] = today.strftime("%B") # June
        email_d["[yearsubmitted]"] = today.strftime("%Y")  # 2010
        email_d["[unsubscribeurl]"] = "[unsubscribeurl]"    
        
        email_d["[currentweekdayname]"] = today.strftime("%A")    # Wednesday
        email_d["[currentday]"] = today.strftime("%d")                       
        email_d["[currentmonthname]"] = today.strftime("%B")
        
        
        
        email = Email()
        is_valid = email.template_body(email_d)
        email.sender_display = "%s %s" % (request.user.first_name, request.user.last_name)
        email.sender = request.user.email
        email.reply_to = request.user.email
        email.recipient = request.user.email
        #email.send_to_email2 
        email.content_type = 'text/html'
        
        personalize_subject_first_name = self.cleaned_data['personalize_subject_first_name']
        personalize_subject_last_name = self.cleaned_data['personalize_subject_last_name']
        
        email.subject = self.cleaned_data['subject']
        if personalize_subject_first_name and personalize_subject_last_name:
            email.subject = "[firstname] [lastname], " + email.subject
        elif personalize_subject_first_name:
            email.subject = "[firstname], " + email.subject
        elif personalize_subject_last_name:
            email.subject = "[lastname], " + email.subject
        email.status = 1
        email.status_detail = 'active'
        email.category = 'marketing'
        
        email.save(request.user)
        
        # action object - these 3 already included on the form: member_only, group and send_to_emails
        now = datetime.datetime.now()
        self.instance.email = email
        self.instance.name = email.subject
        self.instance.type = 'Distribution E-mail'
        self.instance.name = email.subject
        self.instance.description = '%s Electronic Newsletter: generated %s' % \
                            (get_setting('site', "global", "sitedisplayname"), 
                             now.strftime('%d-%b-%y %I:%M:%S %p'))
        self.instance.category = 'marketing'
        self.instance.due_dt = now
        try:
            entity = (request.user.get_profile()).entity
        except:
            entity = None
        if entity:
            self.instance.entity = entity
        self.instance.status = 1
        self.instance.status_detail = 'open'
        self.instance.save(request.user)
        
        return self.instance

        
        