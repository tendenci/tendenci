import datetime
import re
from django.core.urlresolvers import reverse
from site_settings.utils import get_setting
from event_logs.models import EventLog

p = re.compile(r"(href=\")((../)+)([^/])", re.IGNORECASE)

# send 50 emails per connection
EMAILS_PER_CONNECTION = 50

def distribute_newsletter(request, action, **kwargs):
    from django.template.loader import render_to_string
    from django.template import RequestContext
    from django.core import mail
    connection = mail.get_connection()
    
    if action.status_detail == 'open':
        if action.group:
            # update the status_detail first
            action.status_detail = 'inprogress'
            action.start_dt = datetime.datetime.now()
            action.save()
            
            i = 0
            result_d = {'total': 0, 'total_success':0, 'total_failed':0, 'total_nomail':0}
            recap_d = []    # store the result in the action_recap table
            
            email_subject = action.email.subject
            email_body = action.email.body
            
            # if there is [password], replace here
            password_txt = render_to_string('newsletters/password.txt',
                                          context_instance=RequestContext(request))
            
            
            # turn relative links to absolute links
            site_url = get_setting('site', 'global', 'siteurl')
            email_body = email_relativeReftoFQDN(email_body, site_url)
            
            if action.email.content_type == 'text':
                email_body = htmltotext(email_body)
            else:
                # verify if we have the <html> and <body> tags
                email_body = verify_basic_html(email_subject, email_body)
                # remove </body> and </html> - need to append footer to body
                email_body = email_body.replace('</body>', '')
                email_body = email_body.replace('</html>', '')
            
            connection.open()
            
            for user_this in action.group.members.all().order_by('email'):
                result_d['total'] += 1
                direct_mail = (user_this.get_profile()).direct_mail
                
                # if this user opted to not receiving email, skip it
                # but do store his info in the recap_d
                if not direct_mail:
                    recap_d.append({'direct_mail':direct_mail,
                                     'first_name':user_this.first_name,
                                     'last_name':user_this.last_name,
                                     'email':user_this.email,
                                     'id':user_this.id,
                                     'notes':'not delivered - user does not receive email'})
                
                    result_d['total_nomail'] += 1
                    continue
                
                if i > 0 and i % EMAILS_PER_CONNECTION == 0:
                    # make a new connection
                    connection.close()
                    connection.open()
                    i += 1
                    
                profile_this = user_this.get_profile() 
                user_this.password =  password_txt
                subject = customize_subject(email_subject, user_this, profile_this)
                body = customize_body(email_body, user_this, profile_this)
                
                if action.email.content_type <> 'text':
                    action.email.content_type = 'html'
                    footer_template = 'newsletters/footer.html'
                else:
                    footer_template = 'newsletters/footer.txt'
                
                footer = render_to_string(footer_template,
                                          {'action': action,
                                           'user_this': user_this},
                                          context_instance=RequestContext(request))
                # append footer to the body
                body += footer
                if action.email.content_type == 'html':
                    body += "</body></html>"
                
                recipient = [user_this.email]
                if action.send_to_email2:
                    recipient.append(user_this.get_profile().email2)
                
                email = mail.EmailMessage(subject, 
                                  body,
                                  action.email.sender,
                                  recipient,
                                  connection=connection)
                email.content_subtype= action.email.content_type
                boo = email.send()  # send the e-mail
                
                myrecap = {'direct_mail':direct_mail,
                             'first_name':user_this.first_name,
                             'last_name':user_this.last_name,
                             'email':user_this.email,
                             'id':user_this.id}
                if boo:
                    result_d['total_success'] += 1
                    myrecap['notes'] = 'sent'
                else:
                    result_d['total_failed'] += 1
                    myrecap['notes'] = 'bad address or e-mail blocked'
                    
                recap_d.append(myrecap)
                    
            print recap_d 
            # insert the recap_d into table action_recap
             
            connection.close()
            
            # update the status
            action.status_detail = 'closed'
            action.sent = result_d['total_success']
            action.attempted = result_d['total']
            action.failed = result_d['total_failed']+ result_d['total_nomail']
            action.finish_dt = datetime.datetime.now()
            action.save()
            
            # log an event
            log_defaults = {
                'event_id' : 301100,
                'event_data': """<b>Actionid: </b><a href="%s">%d</a>,<br />
                                <b>Action name: </b> %s,<br />
                                <b>Action type: </b> %s,<br />
                                <b>Category: </b> marketing,<br />
                                <b>Description: </b> %s,<br />
                                <b>Distributed to %d users part of user group: </b>%s.<br />
                            """ % (reverse('action.view', args=[action.id]), action.id,
                                   action.name, action.type, action.description,
                                   action.sent, action.group.name),
                'description': '%s newsletter sent' % action._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': action,
            }
            EventLog.objects.log(**log_defaults)
            
def customize_subject(subject, user, profile):
    subject = subject.replace("[name]", '%s %s' % (user.first_name, user.last_name))
    subject = subject.replace("[firstname]", user.first_name)
    subject = subject.replace("[lastname]", user.last_name)
    return subject
    
def customize_body(body, user, profile):
    body = body.replace("[name]", '%s %s' % (user.first_name, user.last_name))
    body = body.replace("[firstname]", user.first_name)
    body = body.replace("[lastname]", user.last_name)
    if profile.company:
        body = body.replace("[company]", profile.company)
    else:
        body = body.replace("[company]",'your company')
    body = body.replace("[displayname]", profile.display_name)
    if user.is_active:
        body = body.replace("[username]", user.username)
        body = body.replace("[password]", user.password)
    else:
        body = body.replace("[username]", '')
        body = body.replace("[password]", '')
    body = body.replace("[title]", profile.position_title)
    body = body.replace("[address]", profile.address)
    body = body.replace("[city]", profile.city)
    body = body.replace("[state]", profile.state)
    body = body.replace("[zip]", profile.zipcode)
    body = body.replace("[phone]", profile.phone)
    body = body.replace("[homephone]", profile.home_phone)
    body = body.replace("[fax]", profile.fax)
    body = body.replace("[email]", user.email)
    
    return body

# replaces file level image, link, etc references with FQDN references         
def email_relativeReftoFQDN(body, site_url):
    # remove ../ or ../../ or ../../../ etc.
    body = p.sub(r'\1/\4', body)
    
    body = body.replace("src=\"/", "src=\"" + site_url + "/")
    body = body.replace("href=\"/", "href=\"" + site_url + "/")
    return body

# turn html into plain text
def htmltotext(html_content):
    # replace <p> and </p> with \n
    p = re.compile(r"<p>|<P>|<p [\d\D\s\S\w\W]*?>")
    mytext = p.sub("\n", html_content)
        
    # replace &nbsp; with " "
    mytext = mytext.replace("&nbsp;", " ")
    mytext = mytext.replace("&#160;", " ")
    mytext = mytext.replace("&lt;BR&gt;", " ")
    mytext = mytext.replace("&amp;", "&")
    mytext = mytext.replace("&#38;", "&")
    mytext = mytext.replace("&#34;", "\"")
    mytext = mytext.replace("<li>", r"\t")
    mytext = mytext.replace("<LI>", r"\t")

    # replace <br>, <br/>, <br /> <BR>, <BR/>, <BR /> with "\n"
    p = re.compile(r"<br>|<br/>|<br />|<BR>|<BR/>|<BR />")
    mytext = p.sub("\n", mytext)
       
    # strip out all html tags
    p = re.compile(r"<[\d\D\s\S\w\W]*?>")
    mytext = p.sub("", mytext)

    # strip out extra space
    p = re.compile(" {2,}")
    mytext = p.sub(" ", mytext)
    mytext = mytext.replace("\n\n", "\n")
        
    return mytext

# wysiwyg strips out the html and body tags from the email.
# so verify if the email body has the html and title tags
# if not, add them
def verify_basic_html(subject, body):
    if body.find("<html>") == -1:
        if body.find("<body>") == -1:
            # no html tag nor body tag
            # test if it contains title and meta tags. if so, remove them
            title_p = re.compile('(<title[^>]*>([\d\D\s\S\w\W]*?)</title>)', re.IGNORECASE)
            body = title_p.sub("", body)
            meta_p = re.compile('(<meta ([\d\D\s\S\w\W]*?) />)', re.IGNORECASE)
            body = meta_p.sub("", body)
            # now we are clean - ready to add body
            body = "<body>\n%s" % (body)
        # add html tag
        body = """
              <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" 
               "http://www.w3.org/TR/html4/loose.dtd">
               <html>
               <head>
               <title>%s</title>
               <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
               </head>
               %s
            """ % (subject, body)
        
    return body
   
