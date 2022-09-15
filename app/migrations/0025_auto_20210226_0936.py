# Generated by Django 2.2.17 on 2021-02-26 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0024_auto_20210224_1219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kotdarepositoryresource',
            name='access_level',
            field=models.CharField(blank=True, choices=[('Public information', 'Public information'), ('Internal ', 'Internal'), ('Restricted', 'Restricted'), ('Confidential', 'Confidential')], default='Internal', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='learningresource',
            name='access_level',
            field=models.CharField(choices=[('Public', 'Public'), ('Protected', 'Protected'), ('Private', 'Private')], default='Internal', max_length=50),
        ),
        migrations.AlterField(
            model_name='learningresourcemodule',
            name='access_level',
            field=models.CharField(choices=[('Public', 'Public'), ('Protected', 'Protected'), ('Private', 'Private')], default='Internal', max_length=50),
        ),
        migrations.AlterField(
            model_name='policy',
            name='access_level',
            field=models.CharField(choices=[('Public information', 'Public information'), ('Internal ', 'Internal'), ('Restricted', 'Restricted'), ('Confidential', 'Confidential')], default='Internal', max_length=50),
        ),
        migrations.AlterField(
            model_name='repositorydocumentfolder',
            name='access_level',
            field=models.CharField(choices=[('Public information', 'Public information'), ('Internal ', 'Internal'), ('Restricted', 'Restricted'), ('Confidential', 'Confidential')], default='Protected', max_length=50),
        ),
        migrations.AlterField(
            model_name='repositoryresourcedownload',
            name='access_level',
            field=models.CharField(choices=[('Public information', 'Public information'), ('Internal ', 'Internal'), ('Restricted', 'Restricted'), ('Confidential', 'Confidential')], default='Public', max_length=50),
        ),
        migrations.AlterField(
            model_name='repositoryresourceimage',
            name='access_level',
            field=models.CharField(choices=[('Public information', 'Public information'), ('Internal ', 'Internal'), ('Restricted', 'Restricted'), ('Confidential', 'Confidential')], default='Public', max_length=50),
        ),
        migrations.AlterField(
            model_name='repositoryresourceimage',
            name='name_of_image',
            field=models.CharField(blank=True, default='UNTITLED', max_length=50, null=True, verbose_name='name of document'),
        ),
        migrations.AlterField(
            model_name='repositoryresourcereferenceurl',
            name='access_level',
            field=models.CharField(choices=[('Public information', 'Public information'), ('Internal ', 'Internal'), ('Restricted', 'Restricted'), ('Confidential', 'Confidential')], default='Public', max_length=50),
        ),
        migrations.AlterField(
            model_name='repositoryresourcevideourl',
            name='access_level',
            field=models.CharField(choices=[('Public information', 'Public information'), ('Internal ', 'Internal'), ('Restricted', 'Restricted'), ('Confidential', 'Confidential')], default='Public', max_length=50),
        ),
    ]
