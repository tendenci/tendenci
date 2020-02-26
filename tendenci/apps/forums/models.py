# -*- coding: utf-8 -*-


from django.core.exceptions import ValidationError
from django.urls import reverse
from django.db import models, transaction, DatabaseError
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now as tznow
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import OneToOneField

from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.perms.models import TendenciBaseModel

from .compat import get_user_model_path, get_username_field, get_atomic_func, slugify
from . import defaults
from .profiles import PybbProfile
from .util import unescape, FilePathGenerator, _get_markup_formatter

from annoying.fields import AutoOneToOneField


@python_2_unicode_compatible
class Category(TendenciBaseModel):
    name = models.CharField(_('Name'), max_length=80)
    position = models.IntegerField(_('Position'), blank=True, default=0)
    hidden = models.BooleanField(_('Hidden'), blank=False, null=False, default=False,
                                 help_text=_('If checked, this category will be visible only for staff and the rest of the permissions below will be ignored'))
    slug = models.SlugField(_("Slug"), max_length=255, unique=True)

    perms = GenericRelation(ObjectPermission,
                            object_id_field="object_id",
                            content_type_field="content_type")

    class Meta(object):
#         permissions = (("view_category", _("Can view forum category")),)
        ordering = ['position']
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name

    def forum_count(self):
        return self.forums.all().count()

    def get_absolute_url(self):
        if defaults.PYBB_NICE_URL:
            return reverse('pybb:category', kwargs={'slug': self.slug, })
        return reverse('pybb:category', kwargs={'pk': self.id})

    @property
    def topics(self):
        return Topic.objects.filter(forum__category=self).select_related()

    @property
    def posts(self):
        return Post.objects.filter(topic__forum__category=self).select_related()


@python_2_unicode_compatible
class Forum(models.Model):
    category = models.ForeignKey(Category, related_name='forums', verbose_name=_('Category'), on_delete=models.CASCADE)
    parent = models.ForeignKey('self', related_name='child_forums', verbose_name=_('Parent forum'),
                               blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(_('Name'), max_length=80)
    position = models.IntegerField(_('Position'), blank=True, default=0)
    description = models.TextField(_('Description'), blank=True)
    moderators = models.ManyToManyField(get_user_model_path(), blank=True, verbose_name=_('Moderators'))
    updated = models.DateTimeField(_('Updated'), blank=True, null=True)
    post_count = models.IntegerField(_('Post count'), blank=True, default=0)
    topic_count = models.IntegerField(_('Topic count'), blank=True, default=0)
    hidden = models.BooleanField(_('Hidden'), blank=False, null=False, default=False)
    readed_by = models.ManyToManyField(get_user_model_path(), through='ForumReadTracker', related_name='readed_forums')
    headline = models.TextField(_('Headline'), blank=True, null=True)
    slug = models.SlugField(verbose_name=_("Slug"), max_length=255)

    class Meta(object):
        ordering = ['position']
        verbose_name = _('Forum')
        verbose_name_plural = _('Forums')
        unique_together = ('category', 'slug')

    def __str__(self):
        return self.name

    def update_counters(self):
        self.topic_count = Topic.objects.filter(forum=self).count()
        if self.topic_count:
            posts = Post.objects.filter(topic__forum_id=self.id)
            self.post_count = posts.count()
            if self.post_count:
                try:
                    last_post = posts.order_by('-created', '-id')[0]
                    self.updated = last_post.updated or last_post.created
                except IndexError:
                    pass
        else:
            self.post_count = 0
        self.save()

    def get_absolute_url(self):
        if defaults.PYBB_NICE_URL:
            return reverse('pybb:forum', kwargs={'slug': self.slug, 'category_slug': self.category.slug})
        return reverse('pybb:forum', kwargs={'pk': self.id})

    @property
    def posts(self):
        return Post.objects.filter(topic__forum=self).select_related()

    @cached_property
    def last_post(self):
        try:
            return self.posts.order_by('-created', '-id')[0]
        except IndexError:
            return None

    def get_parents(self):
        """
        Used in templates for breadcrumb building
        """
        parents = [self.category]
        parent = self.parent
        while parent is not None:
            parents.insert(1, parent)
            parent = parent.parent
        return parents


@python_2_unicode_compatible
class Topic(models.Model):
    POLL_TYPE_NONE = 0
    POLL_TYPE_SINGLE = 1
    POLL_TYPE_MULTIPLE = 2

    POLL_TYPE_CHOICES = (
        (POLL_TYPE_NONE, _('None')),
        (POLL_TYPE_SINGLE, _('Single answer')),
        (POLL_TYPE_MULTIPLE, _('Multiple answers')),
    )

    forum = models.ForeignKey(Forum, related_name='topics', verbose_name=_('Forum'), on_delete=models.CASCADE)
    name = models.CharField(_('Subject'), max_length=255)
    created = models.DateTimeField(_('Created'), null=True)
    updated = models.DateTimeField(_('Updated'), null=True)
    user = models.ForeignKey(get_user_model_path(), verbose_name=_('Owner'), null=True, on_delete=models.SET_NULL)
    views = models.IntegerField(_('Views count'), blank=True, default=0)
    sticky = models.BooleanField(_('Sticky'), blank=True, default=False)
    closed = models.BooleanField(_('Closed'), blank=True, default=False)
    subscribers = models.ManyToManyField(get_user_model_path(), related_name='subscriptions',
                                         verbose_name=_('Subscribers'), blank=True)
    post_count = models.IntegerField(_('Post count'), blank=True, default=0)
    readed_by = models.ManyToManyField(get_user_model_path(), through='TopicReadTracker', related_name='readed_topics')
    on_moderation = models.BooleanField(_('On moderation'), default=False)
    poll_type = models.IntegerField(_('Poll type'), choices=POLL_TYPE_CHOICES, default=POLL_TYPE_NONE)
    poll_question = models.TextField(_('Poll question'), blank=True, null=True)
    slug = models.SlugField(verbose_name=_("Slug"), max_length=255)

    class Meta(object):
        ordering = ['-created']
        verbose_name = _('Topic')
        verbose_name_plural = _('Topics')
        unique_together = ('forum', 'slug')

    def __str__(self):
        return self.name

    @cached_property
    def head(self):
        try:
            return self.posts.all().order_by('created', 'id')[0]
        except IndexError:
            return None

    @cached_property
    def last_post(self):
        try:
            return self.posts.order_by('-created', '-id').select_related('user')[0]
        except IndexError:
            return None

    def get_absolute_url(self):
        if defaults.PYBB_NICE_URL:
            return reverse('pybb:topic', kwargs={'slug': self.slug, 'forum_slug': self.forum.slug, 'category_slug': self.forum.category.slug})
        return reverse('pybb:topic', kwargs={'pk': self.id})

    def save(self, *args, **kwargs):
        if self.id is None:
            self.created = self.updated = tznow()

        forum_changed = False
        old_topic = None
        if self.id is not None:
            old_topic = Topic.objects.get(id=self.id)
            if self.forum != old_topic.forum:
                forum_changed = True

        super(Topic, self).save(*args, **kwargs)

        if forum_changed:
            old_topic.forum.update_counters()
            self.forum.update_counters()

    def delete(self, using=None):
        super(Topic, self).delete(using)
        self.forum.update_counters()

    def update_counters(self):
        self.post_count = self.posts.count()
        # force cache overwrite to get the real latest updated post
        if hasattr(self, 'last_post'):
            del self.last_post
        if self.last_post:
            self.updated = self.last_post.updated or self.last_post.created
        self.save()

    def get_parents(self):
        """
        Used in templates for breadcrumb building
        """
        parents = self.forum.get_parents()
        parents.append(self.forum)
        return parents

    def poll_votes(self):
        if self.poll_type != self.POLL_TYPE_NONE:
            return PollAnswerUser.objects.filter(poll_answer__topic=self).count()
        else:
            return None


class RenderableItem(models.Model):
    """
    Base class for models that has markup, body, body_text and body_html fields.
    """

    class Meta(object):
        abstract = True

    body = models.TextField(_('Message'))
    body_html = models.TextField(_('HTML version'))
    body_text = models.TextField(_('Text version'))

    def render(self):
        self.body_html = _get_markup_formatter()(self.body)
        # Remove tags which was generated with the markup processor
        text = strip_tags(self.body_html)
        # Unescape entities which was generated with the markup processor
        self.body_text = unescape(text)


@python_2_unicode_compatible
class Post(RenderableItem):
    topic = models.ForeignKey(Topic, related_name='posts', verbose_name=_('Topic'), on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model_path(), related_name='posts', verbose_name=_('User'), null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(_('Created'), blank=True, db_index=True)
    updated = models.DateTimeField(_('Updated'), blank=True, null=True)
    user_ip = models.GenericIPAddressField(_('User IP'), default='0.0.0.0')
    on_moderation = models.BooleanField(_('On moderation'), default=False)

    class Meta(object):
        ordering = ['created']
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')

    def summary(self):
        limit = 50
        tail = len(self.body) > limit and '...' or ''
        return self.body[:limit] + tail

    def __str__(self):
        return self.summary()

    def save(self, *args, **kwargs):
        created_at = tznow()
        if self.created is None:
            self.created = created_at
        self.render()

        new = self.pk is None

        topic_changed = False
        old_post = None
        if not new:
            old_post = Post.objects.get(pk=self.pk)
            if old_post.topic != self.topic:
                topic_changed = True

        super(Post, self).save(*args, **kwargs)

        # If post is topic head and moderated, moderate topic too
        if self.topic.head == self and not self.on_moderation and self.topic.on_moderation:
            self.topic.on_moderation = False

        self.topic.update_counters()
        self.topic.forum.update_counters()

        if topic_changed:
            old_post.topic.update_counters()
            old_post.topic.forum.update_counters()

    def get_absolute_url(self):
        return reverse('pybb:post', kwargs={'pk': self.id})

    def delete(self, *args, **kwargs):
        self_id = self.id
        head_post_id = self.topic.posts.order_by('created', 'id')[0].id

        if self_id == head_post_id:
            self.topic.delete()
        else:
            super(Post, self).delete(*args, **kwargs)
            self.topic.update_counters()
            self.topic.forum.update_counters()

    def get_parents(self):
        """
        Used in templates for breadcrumb building
        """
        return self.topic.forum.category, self.topic.forum, self.topic,


class Profile(PybbProfile):
    """
    Profile class that can be used if you doesn't have
    your site profile.
    """
    user = OneToOneField(get_user_model_path(), related_name='pybb_profile', verbose_name=_('User'), on_delete=models.CASCADE)

    class Meta(object):
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

    def get_absolute_url(self):
        return reverse('pybb:user', kwargs={'username': getattr(self.user, get_username_field())})

    def get_display_name(self):
        return self.user.get_username()


class Attachment(models.Model):
    class Meta(object):
        verbose_name = _('Attachment')
        verbose_name_plural = _('Attachments')

    post = models.ForeignKey(Post, verbose_name=_('Post'), related_name='attachments', on_delete=models.CASCADE)
    size = models.IntegerField(_('Size'))
    file = models.FileField(_('File'),
                            upload_to=FilePathGenerator(to=defaults.PYBB_ATTACHMENT_UPLOAD_TO))

    def save(self, *args, **kwargs):
        self.size = self.file.size
        super(Attachment, self).save(*args, **kwargs)

    def size_display(self):
        size = self.size
        if size < 1024:
            return '%db' % size
        elif size < 1024 * 1024:
            return '%dKb' % int(size / 1024)
        else:
            return '%.2fMb' % (size / float(1024 * 1024))


class TopicReadTrackerManager(models.Manager):
    def get_or_create_tracker(self, user, topic):
        """
        Correctly create tracker in mysql db on default REPEATABLE READ transaction mode

        It's known problem when standrard get_or_create method return can raise exception
        with correct data in mysql database.
        See http://stackoverflow.com/questions/2235318/how-do-i-deal-with-this-race-condition-in-django/2235624
        """
        is_new = True
        sid = transaction.savepoint(using=self.db)
        try:
            with get_atomic_func()():
                obj = TopicReadTracker.objects.create(user=user, topic=topic)
            transaction.savepoint_commit(sid)
        except DatabaseError:
            transaction.savepoint_rollback(sid)
            obj = TopicReadTracker.objects.get(user=user, topic=topic)
            is_new = False
        return obj, is_new


class TopicReadTracker(models.Model):
    """
    Save per user topic read tracking
    """
    user = models.ForeignKey(get_user_model_path(), blank=False, null=False, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, blank=True, null=True, on_delete=models.CASCADE)
    time_stamp = models.DateTimeField(auto_now=True)

    objects = TopicReadTrackerManager()

    class Meta(object):
        verbose_name = _('Topic read tracker')
        verbose_name_plural = _('Topic read trackers')
        unique_together = ('user', 'topic')


class ForumReadTrackerManager(models.Manager):
    def get_or_create_tracker(self, user, forum):
        """
        Correctly create tracker in mysql db on default REPEATABLE READ transaction mode

        It's known problem when standrard get_or_create method return can raise exception
        with correct data in mysql database.
        See http://stackoverflow.com/questions/2235318/how-do-i-deal-with-this-race-condition-in-django/2235624
        """
        is_new = True
        sid = transaction.savepoint(using=self.db)
        try:
            with get_atomic_func()():
                obj = ForumReadTracker.objects.create(user=user, forum=forum)
            transaction.savepoint_commit(sid)
        except DatabaseError:
            transaction.savepoint_rollback(sid)
            is_new = False
            obj = ForumReadTracker.objects.get(user=user, forum=forum)
        return obj, is_new


class ForumReadTracker(models.Model):
    """
    Save per user forum read tracking
    """
    user = models.ForeignKey(get_user_model_path(), blank=False, null=False, on_delete=models.CASCADE)
    forum = models.ForeignKey(Forum, blank=True, null=True, on_delete=models.CASCADE)
    time_stamp = models.DateTimeField(auto_now=True)

    objects = ForumReadTrackerManager()

    class Meta(object):
        verbose_name = _('Forum read tracker')
        verbose_name_plural = _('Forum read trackers')
        unique_together = ('user', 'forum')


@python_2_unicode_compatible
class PollAnswer(models.Model):
    topic = models.ForeignKey(Topic, related_name='poll_answers', verbose_name=_('Topic'), on_delete=models.CASCADE)
    text = models.CharField(max_length=255, verbose_name=_('Text'))

    class Meta:
        verbose_name = _('Poll answer')
        verbose_name_plural = _('Polls answers')

    def __str__(self):
        return self.text

    def votes(self):
        return self.users.count()

    def votes_percent(self):
        topic_votes = self.topic.poll_votes()
        if topic_votes > 0:
            return 1.0 * self.votes() / topic_votes * 100
        else:
            return 0


@python_2_unicode_compatible
class PollAnswerUser(models.Model):
    poll_answer = models.ForeignKey(PollAnswer, related_name='users', verbose_name=_('Poll answer'), on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model_path(), related_name='poll_answers', verbose_name=_('User'), on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Poll answer user')
        verbose_name_plural = _('Polls answers users')
        unique_together = (('poll_answer', 'user', ), )

    def __str__(self):
        return '%s - %s' % (self.poll_answer.topic, self.user)


def create_or_check_slug(instance, model, **extra_filters):
    """
    returns a unique slug

    :param instance : target instance
    :param model: needed as instance._meta.model is available since django 1.6
    :param extra_filters: filters needed for Forum and Topic for their unique_together field
    """
    initial_slug = instance.slug or slugify(instance.name)
    count = -1
    last_count_len = 0
    slug_is_not_unique = True
    while slug_is_not_unique:
        count += 1

        if count >= defaults.PYBB_NICE_URL_SLUG_DUPLICATE_LIMIT:
            msg = _('After %(limit)s attemps, there is not any unique slug value for "%(slug)s"')
            raise ValidationError(msg % {'limit': defaults.PYBB_NICE_URL_SLUG_DUPLICATE_LIMIT,
                                         'slug': initial_slug})

        count_len = len(str(count))

        if last_count_len != count_len:
            last_count_len = count_len
            filters = {'slug__startswith': initial_slug[:(254-count_len)], }
            if extra_filters:
                filters.update(extra_filters)
            objs = model.objects.filter(**filters).exclude(pk=instance.pk)
            slug_list = [obj.slug for obj in objs]

        if count == 0:
            slug = initial_slug
        else:
            slug = '%s-%d' % (initial_slug[:(254-count_len)], count)
        slug_is_not_unique = slug in slug_list

    return slug
