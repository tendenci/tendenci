from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0007_auto_20200902_1545'),
    ]

    operations = [
        migrations.AddField(
            model_name='field',
            name='remember',
            field=models.BooleanField(default=False, help_text='Remember the value entered between visits and initialise the form with that value.', verbose_name='Remember'),
        ),
    ]
