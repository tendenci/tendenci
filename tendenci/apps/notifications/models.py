from os.path import splitext
import datetime
import uuid

try:
    import cPickle as pickle
except ImportError:
    import pickle

from django.db import models
from django.db.models.query import QuerySet
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.loader import render_to_string
from django.template import RequestContext
from django.core.mail import EmailMessage

from django.core.exceptions import ImproperlyConfigured
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext, get_language, activate
from django.utils.safestring import mark_safe
from django.utils.html import escape

from tendenci.core.site_settings.utils import get_setting

QUEUE_ALL = getattr(settings, "NOTIFICATION_QUEUE_ALL", False)


class LanguageStoreNotAvailable(Exception):
    pass


class NoticeType(models.Model):

    label = models.CharField(_('label'), max_length=40)
    display = models.CharField(_('display'), max_length=50)
    description = models.CharField(_('description'), max_length=100)

    # by default only on for media with sensitivity less than or equal to this number
    default = models.IntegerField(_('default'))

    def __unicode__(self):
        return self.label

    class Meta:
        verbose_name = _("notice type")
        verbose_name_plural = _("notice types")


# if this gets updated, the create() method below needs to be as well...
NOTICE_MEDIA = (
    ("1", _("Email")),
)

# how spam-sensitive is the medium
NOTICE_MEDIA_DEFAULTS = {
    "1": 2  # email
}


class NoticeSetting(models.Model):
    """
    Indicates, for a given user, whether to send notifications
    of a given type to a given medium.
    """

    user = models.ForeignKey(User, verbose_name=_('user'))
    notice_type = models.ForeignKey(NoticeType, verbose_name=_('notice type'))
    medium = models.CharField(_('medium'), max_length=1, choices=NOTICE_MEDIA)
    send = models.BooleanField(_('send'))

    class Meta:
        verbose_name = _("notice setting")
        verbose_name_plural = _("notice settings")
        unique_together = ("user", "notice_type", "medium")


def get_notification_setting(user, notice_type, medium, *args, **kwargs):
    try:
        return NoticeSetting.objects.get(user=user, notice_type=notice_type, medium=medium)
    except NoticeSetting.DoesNotExist:
        send = kwargs.get('send', False)

        # default = (NOTICE_MEDIA_DEFAULTS[medium] <= notice_type.default)
        default = send  # for now default it to false, they have to opt in to get emails
        setting = NoticeSetting(user=user, notice_type=notice_type, medium=medium, send=default)
        setting.save()
        return setting


def should_send(user, notice_type, medium, *args, **kwargs):
    return get_notification_setting(user, notice_type, medium, *args, **kwargs).send


class NoticeManager(models.Manager):

    def notices_for(self, user, archived=False, unseen=None, on_site=None):
        """
        returns Notice objects for the given user.

        If archived=False, it only include notices not archived.
        If archived=True, it returns all notices for that user.

        If unseen=None, it includes all notices.
        If unseen=True, return only unseen notices.
        If unseen=False, return only seen notices.
        """
        if archived:
            qs = self.filter(user=user)
        else:
            qs = self.filter(user=user, archived=archived)
        if unseen is not None:
            qs = qs.filter(unseen=unseen)
        if on_site is not None:
            qs = qs.filter(on_site=on_site)
        return qs

    def unseen_count_for(self, user, **kwargs):
        """
        returns the number of unseen notices for the given user but does not
        mark them seen
        """
        return self.notices_for(user, unseen=True, **kwargs).count()


class Notice(models.Model):

    user = models.ForeignKey(User, verbose_name=_('user'))
    message = models.TextField(_('message'))
    notice_type = models.ForeignKey(NoticeType, verbose_name=_('notice type'))
    added = models.DateTimeField(_('added'), default=datetime.datetime.now)
    unseen = models.BooleanField(_('unseen'), default=True)
    archived = models.BooleanField(_('archived'), default=False)
    on_site = models.BooleanField(_('on site'))

    objects = NoticeManager()

    def __unicode__(self):
        return self.message

    def archive(self):
        self.archived = True
        self.save()

    def is_unseen(self):
        """
        returns value of self.unseen but also changes it to false.

        Use this in a template to mark an unseen notice differently the first
        time it is shown.
        """
        unseen = self.unseen
        if unseen:
            self.unseen = False
            self.save()
        return unseen

    class Meta:
        ordering = ["-added"]
        verbose_name = _("notice")
        verbose_name_plural = _("notices")

    def get_absolute_url(self):
        return ("notification_notice", [str(self.pk)])
    get_absolute_url = models.permalink(get_absolute_url)


class NoticeQueueBatch(models.Model):
    """
    A queued notice.
    Denormalized data for a notice.
    """
    pickled_data = models.TextField()


class NoticeEmail(models.Model):
    """Saved Emails
    """
    guid = models.CharField(max_length=50)
    sender = models.CharField(max_length=200, blank=True)
    emails = models.CharField(max_length=200, blank=True)
    bcc = models.CharField(max_length=200, blank=True)
    notice_type = models.ForeignKey(NoticeType, verbose_name=_('notice type'))
    reply_to = models.CharField(max_length=100, blank=True)
    from_display = models.CharField(max_length=100, blank=True)
    title = models.TextField(blank=True)
    content = models.TextField(blank=True)
    content_type = models.CharField(max_length=10)
    date_sent = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('notification_email', [self.guid])

    def save(self, *args, **kwargs):
        self.guid = self.guid or unicode(uuid.uuid1())
        super(NoticeEmail, self).save(*args, **kwargs)

    def resend(self):
        headers = {}
        if self.reply_to:
            headers['Reply-To'] = self.reply_to
        if self.from_display:
            headers['From'] = self.from_display

        email_list = []
        for email in self.emails.split(','):
            email_list.append(email)

        if self.bcc:
            email = EmailMessage(self.title,
                                 self.content,
                                 self.sender,
                                 email_list,
                                 self.recipient_bcc,
                                 headers=headers)
        else:
            email = EmailMessage(self.title,
                                 self.content,
                                 self.sender,
                                 email_list,
                                 headers=headers)

        email.content_subtype = self.content_type or 'html'
        return email.send()


def create_notice_type(label, display, description, default=2, verbosity=1):
    """
    Creates a new NoticeType.

    This is intended to be used by other apps as a post_syncdb manangement step.
    """
    [notice_type] = NoticeType.objects.filter(label=label)[:1] or [None]
    if notice_type:
        updated = False
        if display != notice_type.display:
            notice_type.display = display
            updated = True
        if description != notice_type.description:
            notice_type.description = description
            updated = True
        if default != notice_type.default:
            notice_type.default = default
            updated = True
        if updated:
            notice_type.save()
            if verbosity > 1:
                print "Updated %s NoticeType" % label
    else:
        NoticeType(label=label, display=display, description=description, default=default).save()
        if verbosity > 1:
            print "Created %s NoticeType" % label


def get_notification_language(user):
    """
    Returns site-specific notification language for this user. Raises
    LanguageStoreNotAvailable if this site does not use translated
    notifications.
    """
    if getattr(settings, 'NOTIFICATION_LANGUAGE_MODULE', False):
        try:
            app_label, model_name = settings.NOTIFICATION_LANGUAGE_MODULE.split('.')
            model = models.get_model(app_label, model_name)
            language_model = model._default_manager.get(user__id__exact=user.id)
            if hasattr(language_model, 'language'):
                return language_model.language
        except (ImportError, ImproperlyConfigured, model.DoesNotExist):
            raise LanguageStoreNotAvailable
    raise LanguageStoreNotAvailable


def get_formatted_messages(formats, label, context):
    """
    Returns a dictionary with the format identifier as the key. The values are
    are fully rendered templates with the given context.
    """
    format_templates = {}
    for format in formats:
        template_name = splitext(format)[0]
        template_ext = splitext(format)[1]

        if template_ext == '.txt':
            context.autoescape = False
        else:
            context.autoescape = True

        list_of_templates = (
            'notification/%s/%s' % (label, format),
            'notification/%s' % format
        )

        template = render_to_string(list_of_templates, context_instance=context)

        if template_name == 'short':
            template = template.strip()

        format_templates[template_name] = template

    return format_templates


def send_emails(emails, label, extra_context=None, on_site=True):
    """
    This method accepts a list of email addresses
    as opposed to a list of users. This is a custom method
    as opposed to send(), send_now(), and queue()

    Just send the notice to a list of emails immediately.
    No new notice created here
    notification.send_emails(email_list, 'friends_invite_sent', {
        'spam': 'eggs',
        'foo': 'bar',
    )
    """
    if extra_context is None:
        extra_context = {}

    try:
        notice_type = NoticeType.objects.get(label=label)
    except:
        # Stop here because we need a notice_type
        return None

    headers = {}
    protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
    current_site = Site.objects.get_current()

    notices_url = u"%s://%s%s" % (
        protocol,
        unicode(current_site),
        reverse("notification_notices"),
    )

    formats = (
        'full.html',
        'short.txt',
        'notice.html',
    )  # TODO make formats configurable

    # test for request in the extra_context
    if 'request' in extra_context.keys():
        context = RequestContext(extra_context['request'])
        extra_context.update({
            "notice": ugettext(notice_type.display),
            "notices_url": notices_url,
            "current_site": current_site,
        })
        context.update(extra_context)
    else:
        # update context with user specific translations
        context = Context({
            "notice": ugettext(notice_type.display),
            "notices_url": notices_url,
            "current_site": current_site,
        })
        context.update(extra_context)

    # get prerendered format messages
    messages = get_formatted_messages(formats, label, context)

    if 'admin' in label:
        subject = messages['short']
        body = messages['full']

    else:
        subject = render_to_string(
            'notification/email_subject.txt',
            {'message': mark_safe(messages['short'])},
            context)

        body = render_to_string(
            'notification/email_body.txt',
            {'message': mark_safe(messages['full'])},
            context)

    if 'reply_to' in extra_context.keys():
        reply_to = extra_context['reply_to']
        headers['Reply-To'] = reply_to
    else:
        reply_to = ''

    sender = extra_context.get('sender', '')
    if not sender:
        sender = get_setting('site', 'global', 'siteemailnoreplyaddress') or settings.DEFAULT_FROM_EMAIL
        if not sender:
            sender = settings.DEFAULT_FROM_EMAIL

    sender_display = extra_context.get('sender_display', '')
    from_display = '%s<%s>' % (sender_display, sender)

    if sender_display:
        headers['From'] = from_display

    recipient_bcc = extra_context.get('recipient_bcc') or []
    content_type = 'html'

    # removing newlines
    subject = ''.join(subject.splitlines())

    for email_addr in emails:
        recipients = [email_addr]

        if recipient_bcc:
            email = EmailMessage(subject, body, sender,
                                 recipients, recipient_bcc, headers=headers)
        else:
            email = EmailMessage(subject, body, sender,
                                 recipients, headers=headers)
        email.content_subtype = content_type

        try:
            email.send(fail_silently=True)  # should we raise exception or not?
        except UnicodeError:
            pass

    to = ','.join(emails)
    bcc = ','.join(recipient_bcc)
    reply_to = reply_to or unicode()

    NoticeEmail.objects.create(
        emails=to,
        sender=sender,
        bcc=bcc,
        title=subject,
        content=body,
        reply_to=reply_to,
        from_display=from_display,
        notice_type=notice_type
    )


def send_now(users, label, extra_context=None, on_site=True, *args, **kwargs):
    """
    Creates a new notice.

    This is intended to be how other apps create new notices.

    notification.send(user, 'friends_invite_sent', {
        'spam': 'eggs',
        'foo': 'bar',
    )

    You can pass in on_site=False to prevent the notice emitted from being
    displayed on the site.
    """

    send = kwargs.get('send', False)

    if extra_context is None:
        extra_context = {}

    try:
        notice_type = NoticeType.objects.get(label=label)
    except (NoticeType.DoesNotExist, NoticeType.MultipleObjectsReturned):
        notice_type = None

    if notice_type:

        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        current_site = Site.objects.get_current()

        notices_url = u"%s://%s%s" % (
            protocol,
            unicode(current_site),
            reverse("notification_notices"),
        )

        current_language = get_language()

        formats = (
            'full.html',
            'short.txt',
            'notice.html',
        )  # TODO make formats configurable

        for user in users:
            recipients = []
            headers = {}
            # get user language for user from language store defined in
            # NOTIFICATION_LANGUAGE_MODULE setting
            try:
                language = get_notification_language(user)
            except LanguageStoreNotAvailable:
                language = None

            if language is not None:
                # activate the user's language
                activate(language)

            # test for request in the extra_context
            if 'request' in extra_context.keys():
                context = RequestContext(extra_context['request'])
                extra_context.update({
                    "user": user,
                    "notice": ugettext(notice_type.display),
                    "notices_url": notices_url,
                    "current_site": current_site,
                })
                context.update(extra_context)
            else:
                # update context with user specific translations
                context = Context({
                    "user": user,
                    "notice": ugettext(notice_type.display),
                    "notices_url": notices_url,
                    "current_site": current_site,
                })
                context.update(extra_context)

            # get prerendered format messages
            messages = get_formatted_messages(formats, label, context)

            # Strip newlines from subject
            subject = ''.join(render_to_string('notification/email_subject.txt', {
                'message': messages['short'][0],
            }, context).splitlines())

            body = render_to_string('notification/email_body.txt', {
                'message': messages['full'][0],
            }, context)

            Notice.objects.create(user=user,
                                  message=messages['notice'][0],
                                  notice_type=notice_type,
                                  on_site=on_site)
            if should_send(user, notice_type, "1", send=send) and user.email:  # Email
                recipients.append(user.email)

            if messages['full'][1] == '.html':
                # headers = {'Content-Type': 'text/html'}
                content_type = 'html'
            else:
                # headers = {'Content-Type': 'text/plain'}
                content_type = 'text'

            email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, recipients, headers=headers)
            email.content_subtype = content_type
            email.send()

        # reset environment to original language
        activate(current_language)


def send(*args, **kwargs):
    """
    A basic interface around both queue and send_now. This honors a global
    flag NOTIFICATION_QUEUE_ALL that helps determine whether all calls should
    be queued or not. A per call ``queue`` or ``now`` keyword argument can be
    used to always override the default global behavior.
    """
    queue_flag = kwargs.pop("queue", False)
    now_flag = kwargs.pop("now", False)
    assert not (queue_flag and now_flag), "'queue' and 'now' cannot both be True."
    if queue_flag:
        return queue(*args, **kwargs)
    elif now_flag:
        return send_now(*args, **kwargs)
    else:
        if QUEUE_ALL:
            return queue(*args, **kwargs)
        else:
            return send_now(*args, **kwargs)


def queue(users, label, extra_context=None, on_site=True):
    """
    Queue the notification in NoticeQueueBatch. This allows for large amounts
    of user notifications to be deferred to a seperate process running outside
    the webserver.
    """
    if extra_context is None:
        extra_context = {}
    if isinstance(users, QuerySet):
        users = [row["pk"] for row in users.values("pk")]
    else:
        users = [user.pk for user in users]
    notices = []
    for user in users:
        notices.append((user, label, extra_context, on_site))
    NoticeQueueBatch(pickled_data=pickle.dumps(notices).encode("base64")).save()


class ObservedItemManager(models.Manager):

    def all_for(self, observed, signal):
        """
        Returns all ObservedItems for an observed object,
        to be sent when a signal is emited.
        """
        content_type = ContentType.objects.get_for_model(observed)
        observed_items = self.filter(content_type=content_type, object_id=observed.id, signal=signal)
        return observed_items

    def get_for(self, observed, observer, signal):
        content_type = ContentType.objects.get_for_model(observed)
        observed_item = self.get(content_type=content_type, object_id=observed.id, user=observer, signal=signal)
        return observed_item


class ObservedItem(models.Model):

    user = models.ForeignKey(User, verbose_name=_('user'))

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    observed_object = generic.GenericForeignKey('content_type', 'object_id')

    notice_type = models.ForeignKey(NoticeType, verbose_name=_('notice type'))

    added = models.DateTimeField(_('added'), default=datetime.datetime.now)

    # the signal that will be listened to send the notice
    signal = models.TextField(verbose_name=_('signal'))

    objects = ObservedItemManager()

    class Meta:
        ordering = ['-added']
        verbose_name = _('observed item')
        verbose_name_plural = _('observed items')

    def send_notice(self):
        send([self.user], self.notice_type.label,
             {'observed': self.observed_object})


def observe(observed, observer, notice_type_label, signal='post_save'):
    """
    Create a new ObservedItem.

    To be used by applications to register a user as an observer for some object.
    """
    notice_type = NoticeType.objects.get(label=notice_type_label)
    observed_item = ObservedItem(user=observer, observed_object=observed,
                                 notice_type=notice_type, signal=signal)
    observed_item.save()
    return observed_item


def stop_observing(observed, observer, signal='post_save'):
    """
    Remove an observed item.
    """
    observed_item = ObservedItem.objects.get_for(observed, observer, signal)
    observed_item.delete()


def send_observation_notices_for(observed, signal='post_save'):
    """
    Send a notice for each registered user about an observed object.
    """
    observed_items = ObservedItem.objects.all_for(observed, signal)
    for observed_item in observed_items:
        observed_item.send_notice()
    return observed_items


def is_observing(observed, observer, signal='post_save'):
    if isinstance(observer, AnonymousUser):
        return False
    try:
        observed_items = ObservedItem.objects.get_for(observed, observer, signal)
        return True
    except ObservedItem.DoesNotExist:
        return False
    except ObservedItem.MultipleObjectsReturned:
        return True


def handle_observations(sender, instance, *args, **kw):
    send_observation_notices_for(instance)
