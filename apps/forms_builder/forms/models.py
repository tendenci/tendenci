
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext, ugettext_lazy as _

from forms_builder.forms.settings import FIELD_MAX_LENGTH, LABEL_MAX_LENGTH
from haystack.query import SearchQuerySet
from perms.utils import is_admin
from perms.models import TendenciBaseModel 

#STATUS_DRAFT = 1
#STATUS_PUBLISHED = 2
STATUS_CHOICES = (
    ('draft', "Draft"), 
    ('published', "Published"),
)

FIELD_CHOICES = (
    ("CharField", _("Text")),
    ("CharField/django.forms.Textarea", _("Paragraph Text")),
    ("BooleanField", _("Checkbox")),
    ("ChoiceField", _("Choose from a list")),
    ("MultipleChoiceField", _("Multi select")),
    ("EmailField", _("Email")),
    ("FileField", _("File upload")),
    ("DateField/django.forms.extras.SelectDateWidget", _("Date")),
    ("DateTimeField", _("Date/time")),
)

class FormManager(models.Manager):
    """
    Only show published forms for non-staff users.
    """
    def published(self, for_user=None):
        if for_user is not None and for_user.is_staff:
            return self.all()
        return self.filter(status_detail='published')
    
    def search(self, query=None, *args, **kwargs):
        """
            Uses haystack to query news. 
            Returns a SearchQuerySet
        """
        sqs = SearchQuerySet()
        user = kwargs.get('user', None)
        is_an_admin = is_admin(user)
            
        if query:
            sqs = sqs.auto_query(sqs.query.clean(query)) 
            if user:
                if not is_an_admin:
                    return []
        else:
            sqs = sqs.all()
            if user:
                if not is_an_admin:
                    return []
    
        return sqs.models(self.model).order_by('-create_dt')
    
class Form(TendenciBaseModel):
    """
    A user-built form.
    """

    title = models.CharField(_("Title"), max_length=50)
    slug = models.SlugField(editable=False, max_length=100, unique=True)
    intro = models.TextField(_("Intro"), max_length=2000)
    response = models.TextField(_("Response"), max_length=2000)
#    status = models.IntegerField(_("Status"), choices=STATUS_CHOICES, 
#        default=STATUS_PUBLISHED)
    send_email = models.BooleanField(_("Send email"), default=True, help_text=
        _("If checked, the person entering the form will be sent an email"))
    email_from = models.EmailField(_("From address"), blank=True, 
        help_text=_("The address the email will be sent from"))
    email_copies = models.CharField(_("Send copies to"), blank=True, 
        help_text=_("One or more email addresses, separated by commas"), 
        max_length=200)

    objects = FormManager()

    class Meta:
        verbose_name = _("Form")
        verbose_name_plural = _("Forms")
        permissions = (("view_form","Can view form"),)
    
    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Create a unique slug from title - append an index and increment if it 
        already exists.
        """
        if not self.slug:
            self.slug = slugify(self.title)
            i = 0
            while True:
                if i > 0:
                    if i > 1:
                        self.slug = self.slug.rsplit("-", 1)[0]
                    self.slug = "%s-%s" % (self.slug, i)
                if not Form.objects.filter(slug=self.slug):
                    break
                i += 1
        super(Form, self).save(*args, **kwargs)
        
    @models.permalink
    def get_absolute_url(self):
        return ("form_detail", (), {"slug": self.slug})

    def admin_link_view(self):
        url = self.get_absolute_url()
        return "<a href='%s'>%s</a>" % (url, ugettext("View on site"))
    admin_link_view.allow_tags = True
    admin_link_view.short_description = ""

    def admin_link_export(self):
        url = reverse("admin:form_export", args=(self.id,))
        return "<a href='%s'>%s</a>" % (url, ugettext("Export entries"))
    admin_link_export.allow_tags = True
    admin_link_export.short_description = ""

class FieldManager(models.Manager):
    """
    Only show visible fields when displaying actual form..
    """
    def visible(self):
        return self.filter(visible=True)

class Field(models.Model):
    """
    A field for a user-built form.
    """
    
    form = models.ForeignKey("Form", related_name="fields")
    label = models.CharField(_("Label"), max_length=LABEL_MAX_LENGTH)
    field_type = models.CharField(_("Type"), choices=FIELD_CHOICES, 
        max_length=50)
    required = models.BooleanField(_("Required"), default=True)
    visible = models.BooleanField(_("Visible"), default=True)
    choices = models.CharField(_("Choices"), max_length=1000, blank=True, 
        help_text="Comma separated options where applicable")
        
    objects = FieldManager()

    class Meta:
        verbose_name = _("Field")
        verbose_name_plural = _("Fields")
        order_with_respect_to = "form"
    
    def __unicode__(self):
        return self.label

class FormEntry(models.Model):
    """
    An entry submitted via a user-built form.
    """

    form = models.ForeignKey("Form", related_name="entries")
    entry_time = models.DateTimeField(_("Date/time"))
    
    class Meta:
        verbose_name = _("Form entry")
        verbose_name_plural = _("Form entries")

    @models.permalink
    def get_absolute_url(self):
        return ("form_entry_detail", (), {"id": self.pk})
    
class FieldEntry(models.Model):
    """
    A single field value for a form entry submitted via a user-built form.
    """
    
    entry = models.ForeignKey("FormEntry", related_name="fields")
    field = models.ForeignKey("Field", related_name="field")
    value = models.CharField(max_length=FIELD_MAX_LENGTH)

    class Meta:
        verbose_name = _("Form field entry")
        verbose_name_plural = _("Form field entries")

