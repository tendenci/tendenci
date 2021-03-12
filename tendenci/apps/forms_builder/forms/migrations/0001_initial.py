# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(default=0, null=True, verbose_name='Position', blank=True)),
                ('label', models.CharField(max_length=2000, verbose_name='Label')),
                ('field_type', models.CharField(max_length=64, verbose_name='Type', choices=[('CharField', 'Text'), ('CharField/django.forms.Textarea', 'Paragraph Text'), ('BooleanField', 'Checkbox'), ('ChoiceField/django.forms.RadioSelect', 'Single-select - Radio Button'), ('ChoiceField', 'Single-select - From a List'), ('MultipleChoiceField/django.forms.CheckboxSelectMultiple', 'Multi-select - Checkboxes'), ('MultipleChoiceField', 'Multi-select - From a List'), ('EmailVerificationField', 'Email'), ('CountryField', 'Countries'), ('StateProvinceField', 'States/Provinces'), ('FileField', 'File upload'), ('DateField/django.forms.widgets.SelectDateWidget', 'Date - Select'), ('DateField/django.forms.DateInput', 'Date - Text Input'), ('DateTimeField', 'Date/time'), ('CharField/tendenci.apps.forms_builder.forms.widgets.Description', 'Description'), ('CharField/tendenci.apps.forms_builder.forms.widgets.Header', 'Section Heading')])),
                ('field_function', models.CharField(blank=True, max_length=64, null=True, verbose_name='Special Functionality', choices=[('GroupSubscription', 'Subscribe to Group'), ('GroupSubscriptionAuto', 'Subscribe to Group'), ('EmailFirstName', 'First Name'), ('EmailLastName', 'Last Name'), ('EmailFullName', 'Full Name'), ('EmailPhoneNumber', 'Phone Number'), ('Recipients', 'Email to Recipients')])),
                ('required', models.BooleanField(default=True, verbose_name='Required')),
                ('visible', models.BooleanField(default=True, verbose_name='Visible')),
                ('choices', models.CharField(help_text='Comma separated options where applicable', max_length=1000, verbose_name='Choices', blank=True)),
                ('default', models.CharField(help_text='Default value of the field', max_length=1000, verbose_name='Default', blank=True)),
            ],
            options={
                'verbose_name': 'Field',
                'verbose_name_plural': 'Fields',
            },
        ),
        migrations.CreateModel(
            name='FieldEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=2000)),
            ],
            options={
                'verbose_name': 'Form field entry',
                'verbose_name_plural': 'Form field entries',
            },
        ),
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('allow_anonymous_view', models.BooleanField(default=True, verbose_name='Public can view')),
                ('allow_user_view', models.BooleanField(default=True, verbose_name='Signed in user can view')),
                ('allow_member_view', models.BooleanField(default=True)),
                ('allow_user_edit', models.BooleanField(default=False, verbose_name='Signed in user can change')),
                ('allow_member_edit', models.BooleanField(default=False)),
                ('create_dt', models.DateTimeField(auto_now_add=True, verbose_name='Created On')),
                ('update_dt', models.DateTimeField(auto_now=True, verbose_name='Last Updated')),
                ('creator_username', models.CharField(max_length=50)),
                ('owner_username', models.CharField(max_length=50)),
                ('status', models.BooleanField(default=True, verbose_name='Active')),
                ('status_detail', models.CharField(default='active', max_length=50)),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('slug', models.SlugField(unique=True, max_length=100)),
                ('intro', models.TextField(max_length=2000, verbose_name='Intro', blank=True)),
                ('response', models.TextField(max_length=2000, verbose_name='Confirmation Text', blank=True)),
                ('email_text', models.TextField(default='', help_text='If Send email is checked, this is the text that will be sent in an email to the person submitting the form.', max_length=2000, verbose_name='Email Text to Submitter', blank=True)),
                ('subject_template', models.CharField(default='[title] - [first name]  [last name] - [phone]', max_length=200, blank=True, help_text='Options include [title] for form title, and\n                        name of form fields inside brackets [ ]. E.x. [first name] or\n                        [email address]', null=True, verbose_name='Template for email subject ')),
                ('send_email', models.BooleanField(default=False, help_text='If checked, the person submitting the form will be sent an email.', verbose_name='Send email')),
                ('email_from', models.EmailField(help_text='Used as the Reply-to email address in the email to the submitter.', max_length=254, verbose_name='Reply-To address', blank=True)),
                ('email_copies', models.CharField(help_text='One or more email addresses for form recipients, separated by commas', max_length=2000, verbose_name='Send copies to', blank=True)),
                ('completion_url', models.CharField(help_text='Redirect to this page after form completion. Absolute URLS should begin with http. Relative URLs should begin with a forward slash (/).', max_length=1000, null=True, verbose_name='Completion URL', blank=True)),
                ('template', models.CharField(max_length=50, verbose_name='Template', blank=True)),
                ('custom_payment', models.BooleanField(default=False, help_text='If checked, please add pricing options below. Leave the price blank if users can enter their own amount.', verbose_name='Is Custom Payment')),
                ('recurring_payment', models.BooleanField(default=False, help_text="If checked, please add pricing options below. Leave the price blank if users can enter their own amount. Please also add an email field as a required field with type 'email'", verbose_name='Is Recurring Payment')),
                ('intro_position', models.IntegerField(default=1, verbose_name='Intro Position', choices=[(1, 'First'), (2, 'Middle'), (3, 'Last')])),
                ('fields_position', models.IntegerField(default=2, verbose_name='Fields Position', choices=[(1, 'First'), (2, 'Middle'), (3, 'Last')])),
                ('pricing_position', models.IntegerField(default=3, verbose_name='Pricing Position', choices=[(1, 'First'), (2, 'Middle'), (3, 'Last')])),
                ('intro_name', models.CharField(default='Intro', max_length=50, verbose_name='Intro Name', blank=True)),
                ('fields_name', models.CharField(default='Fields', max_length=50, verbose_name='Fields Name', blank=True)),
                ('pricing_name', models.CharField(default='Pricings', max_length=50, verbose_name='Pricing Name', blank=True)),
                ('creator', models.ForeignKey(related_name='forms_form_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity', models.ForeignKey(related_name='forms_form_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True)),
                ('owner', models.ForeignKey(related_name='forms_form_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True)),
                ('payment_methods', models.ManyToManyField(to='payments.PaymentMethod', blank=True)),
            ],
            options={
                'verbose_name': 'Form',
                'verbose_name_plural': 'Forms',
            },
        ),
        migrations.CreateModel(
            name='FormEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('entry_time', models.DateTimeField(verbose_name='Date/time')),
                ('entry_path', models.CharField(default='', max_length=200, blank=True)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('update_dt', models.DateTimeField(auto_now=True)),
                ('creator', models.ForeignKey(related_name='formentry_creator', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('form', models.ForeignKey(related_name='entries', to='forms.Form', on_delete=django.db.models.deletion.CASCADE)),
                ('payment_method', models.ForeignKey(to='payments.PaymentMethod', null=True, on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'verbose_name': 'Form entry',
                'verbose_name_plural': 'Form entries',
            },
        ),
        migrations.CreateModel(
            name='Pricing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=100)),
                ('description', models.TextField(verbose_name='Pricing Description', blank=True)),
                ('price', models.DecimalField(help_text='Leaving this field blank allows visitors to set their own price', null=True, max_digits=10, decimal_places=2, blank=True)),
                ('taxable', models.BooleanField(default=False)),
                ('tax_rate', models.DecimalField(default=0, help_text='Example: 0.0825 for 8.25%.', max_digits=5, decimal_places=4, blank=True)),
                ('billing_period', models.CharField(default='month', max_length=50, choices=[('month', 'Month(s)'), ('year', 'Year(s)'), ('week', 'Week(s)'), ('day', 'Day(s)')])),
                ('billing_frequency', models.IntegerField(default=1)),
                ('num_days', models.IntegerField(default=0)),
                ('due_sore', models.CharField(default='start', max_length=20, verbose_name='Billing cycle start or end date', choices=[('start', 'start'), ('end', 'end')])),
                ('has_trial_period', models.BooleanField(default=False)),
                ('trial_period_days', models.IntegerField(default=0)),
                ('trial_amount', models.DecimalField(default=0.0, null=True, max_digits=15, decimal_places=2, blank=True)),
                ('form', models.ForeignKey(to='forms.Form', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'ordering': ['pk'],
            },
        ),
        migrations.AddField(
            model_name='formentry',
            name='pricing',
            field=models.ForeignKey(to='forms.Pricing', null=True, on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='fieldentry',
            name='entry',
            field=models.ForeignKey(related_name='fields', to='forms.FormEntry', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='fieldentry',
            name='field',
            field=models.ForeignKey(related_name='field', to='forms.Field', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='field',
            name='form',
            field=models.ForeignKey(related_name='fields', to='forms.Form', on_delete=django.db.models.deletion.CASCADE),
        ),
    ]
