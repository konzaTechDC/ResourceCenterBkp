# Generated by Django 2.2.17 on 2021-01-14 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_repositoryresourcevideourl_thumbnail'),
    ]

    operations = [
        migrations.AddField(
            model_name='repositorydocumenttype',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
