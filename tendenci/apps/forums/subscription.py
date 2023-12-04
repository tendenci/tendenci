

from django.conf import settings
from django.urls import reverse
from django.core.validators import validate_email
from django.template.loader import render_to_string
from django.utils import translation
from django.contrib.sites.models import Site
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.base.utils import add_tendenci_footer
from tendenci.apps.emails.models import Email

from . import defaults, util, compat
from .models import ForumSubscription

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

    message = render_to_string(template_name='pybb/mail_templates/subscription_email_body.html',
                               context=kwargs)
    return message.strip()


def notify_forum_subscribers(topic):
    forum = topic.forum
    qs = ForumSubscription.objects.exclude(user=topic.user).filter(forum=topic.forum)
    notifications = qs.filter(type=ForumSubscription.TYPE_NOTIFY)
    if notifications.count():
        users = (n.user for n in notifications.select_related('user'))
        context = {
            'manage_url': reverse('pybb:forum_subscription', kwargs={'pk': forum.id}),
            'topic': topic,
            'site_url': get_setting('site', 'global', 'siteurl'),
        }
        send_notification(users, 'forum_subscription_email', context)
    subscriptions = qs.filter(type=ForumSubscription.TYPE_SUBSCRIBE)
    if subscriptions.count():
        users = (s.user for s in subscriptions.select_related('user'))
        topic.subscribers.add(*users)


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

    subject = render_to_string(template_name=subject_template,
                                   context={'site_url': context_vars['site_url'],
                                    'post': post,
                                    'topic': topic})
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())

    for user in users:
        if Email.is_blocked(user.email):
            continue
        message = get_email_message(user, **context_vars)
        if message:
            message = add_tendenci_footer(message, content_type="text")
            mails += ((subject, message, from_email, [user.email]),)

    # Send mails
    send_mass_mail(mails, fail_silently=True)

    # Reactivate previous language
    translation.activate(old_lang)


def send_notification(users, template, context={}):
    if not 'site' in context:
        context['site'] = Site.objects.get_current()
    context['site_url'] = get_setting('site', 'global', 'siteurl')
    old_lang = translation.get_language()
    from_email = settings.DEFAULT_FROM_EMAIL

    subject = render_to_string('pybb/mail_templates/%s_subject.html' % template, context)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())

    mails = tuple()
    for user in users:
        if Email.is_blocked(user.email):
            continue
        try:
            validate_email(user.email)
        except:
            # Invalid email
            continue

        if user.email == '%s@example.com' % getattr(user, compat.get_username_field()):
            continue

        lang = util.get_pybb_profile(user).language or settings.LANGUAGE_CODE
        translation.activate(lang)

        context['user'] = user
        message = render_to_string('pybb/mail_templates/%s_body.html' % template, context)
        mails += ((subject, message, from_email, [user.email]),)

    # Send mails
    send_mass_mail(mails, fail_silently=True)

    # Reactivate previous language
    translation.activate(old_lang)
