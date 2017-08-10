# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.template.loader import render_to_string
from django.utils import translation
from django.contrib.sites.models import Site
from tendenci.apps.site_settings.utils import get_setting

from . import defaults, util, compat

if defaults.PYBB_USE_DJANGO_MAILER:
    try:
        from mailer import send_mass_mail
    except ImportError:
        from django.core.mail import send_mass_mail
else:
    from django.core.mail import send_mass_mail


def get_email_message(user, **kwargs):
    try:
        validate_email(user.email)
    except:
        # Invalid email
        return

    if user.email == '%s@example.com' % getattr(user, compat.get_username_field()):
        return

    lang = util.get_pybb_profile(user).language or settings.LANGUAGE_CODE
    translation.activate(lang)

    message = render_to_string('pybb/mail_templates/subscription_email_body.html',
                               kwargs)
    return message

def notify_topic_subscribers(post):
    topic = post.topic
    old_lang = translation.get_language()

    # Define constants for templates rendering
    context_vars = {'delete_url': reverse('pybb:delete_subscription', args=[post.topic.id]),
                    'site_url': get_setting('site', 'global', 'siteurl'),
                    'is_new_topic': post == topic.head,
                    'post': post,
                    'post_url': reverse('pybb:post', args=[post.id]),
                    'forum_url': reverse('pybb:forum', args=[topic.forum.id]),
                    }
    from_email = settings.DEFAULT_FROM_EMAIL

    mails = tuple()
    if post == topic.head:
        subject_template = 'pybb/mail_templates/moderator_email_subject.html'
        users = topic.forum.moderators.all()
    else:
        subject_template = 'pybb/mail_templates/subscription_email_subject.html'
        users = topic.subscribers.exclude(pk=post.user.pk)
        
    subject = render_to_string(subject_template,
                                   {'site_url': context_vars['site_url'],
                                    'post': post,
                                    'topic': topic})
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    
    for user in users:
        message = get_email_message(user, **context_vars)
        if message:
            mails += ((subject, message, from_email, [user.email]),)

    # Send mails
    send_mass_mail(mails, fail_silently=True)

    # Reactivate previous language
    translation.activate(old_lang)
