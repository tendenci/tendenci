

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email_blocks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailblock',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]
