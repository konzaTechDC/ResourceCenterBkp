# Generated by Django 2.2.17 on 2021-01-14 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_auto_20210114_2302'),
    ]

    operations = [
        migrations.AddField(
            model_name='repositorydocumenttype',
            name='description',
            field=models.TextField(blank=True, max_length=50000, null=True, verbose_name='description'),
        ),
    ]
