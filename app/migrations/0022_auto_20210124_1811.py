# Generated by Django 2.2.17 on 2021-01-24 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_auto_20210124_1738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='description',
            field=models.TextField(blank=True, max_length=500, null=True, verbose_name='description'),
        ),
    ]
