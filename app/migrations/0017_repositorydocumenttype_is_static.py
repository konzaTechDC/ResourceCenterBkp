<<<<<<< HEAD
# Generated by Django 2.2.17 on 2021-01-15 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_repositorydocumenttype_access_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='repositorydocumenttype',
            name='is_static',
            field=models.BooleanField(default=False),
        ),
    ]
=======
# Generated by Django 2.2.17 on 2021-01-15 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_repositorydocumenttype_access_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='repositorydocumenttype',
            name='is_static',
            field=models.BooleanField(default=False),
        ),
    ]
>>>>>>> deployment-backup
