import uuid
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.translation import ugettext_lazy as _

from timezone_field import TimeZoneField

from tendenci.apps.base.utils import get_timezone_choices
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.contacts.managers import ContactManager


class Address(models.Model):
    address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zipcode = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    class Meta:
        app_label = 'contacts'

    def city_state(self):
        return [s for s in (self.city, self.state) if s]


class Phone(models.Model):
    number = models.CharField(max_length=50, blank=True)

    class Meta:
        app_label = 'contacts'


class Email(models.Model):
    email = models.EmailField()

    class Meta:
        app_label = 'contacts'

class URL(models.Model):
    url = models.URLField()

    class Meta:
        app_label = 'contacts'

class Company(models.Model):
    name = models.CharField(max_length=200, blank=True)
    addresses = models.ManyToManyField(Address, blank=True)
    phones = models.ManyToManyField(Phone, blank=True)
    emails = models.ManyToManyField(Email, blank=True)
    urls = models.ManyToManyField(URL, blank=True)

    class Meta:
        app_label = 'contacts'

class Comment(models.Model):
    """
    Comments made after the contact has been created.
    Contacts will fill out a form and leave a message.
    These comments are added later to help describe the contact.
    """
    contact = models.ForeignKey('Contact', related_name='comments', on_delete=models.CASCADE)
    comment = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    update_dt = models.DateTimeField(auto_now=True)
    create_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'contacts'

class Contact(TendenciBaseModel):
    """
    Contact records are created when someone fills out a form.
    The form creates the contact with a message.
    Later the contact can be updated to include comments for
    further communication.
    """
    guid = models.CharField(max_length=40)
    timezone = TimeZoneField(verbose_name=_('Time Zone'), default='US/Central', choices=get_timezone_choices(), max_length=100)
    user = models.ForeignKey(User, null=True, related_name='contact_user', on_delete=models.CASCADE)

    first_name = models.CharField(max_length=100, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    suffix = models.CharField(max_length=5, blank=True)

    addresses = models.ManyToManyField(Address, blank=True)
    phones = models.ManyToManyField(Phone, blank=True)
    emails = models.ManyToManyField(Email, blank=True)
    urls = models.ManyToManyField(URL, blank=True)
    companies = models.ManyToManyField(Company, blank=True)

    message = models.TextField()

    perms = GenericRelation(ObjectPermission,
        object_id_field="object_id", content_type_field="content_type")

    # TODO: consider attachments

    objects = ContactManager()

    class Meta:
#         permissions = (("view_contact", _("Can view contact")),)
        app_label = 'contacts'

    def get_absolute_url(self):
        return reverse('contact', args=[self.pk])

    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid4())

        super(Contact, self).save(*args, **kwargs)

    def __str__(self):
        if self.first_name:
            return '%s %s' % (self.first_name, self.last_name)
        else:
            return '%s' % self.user
