<<<<<<< HEAD
# Generated by Django 2.2.17 on 2021-01-08 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20210108_1508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kotdarepositoryresource',
            name='type',
            field=models.CharField(blank=True, choices=[('Investor journey', 'Investor journey'), ('Key events', 'Key events'), ('Project milestones', 'Project milestones'), ('Innovation ecosystem', 'Innovation ecosystem'), ('Miscellaneous', 'Miscellaneous')], default='unspecified', max_length=50, null=True),
        ),
    ]
=======
# Generated by Django 2.2.17 on 2021-01-08 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20210108_1508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kotdarepositoryresource',
            name='type',
            field=models.CharField(blank=True, choices=[('Investor journey', 'Investor journey'), ('Key events', 'Key events'), ('Project milestones', 'Project milestones'), ('Innovation ecosystem', 'Innovation ecosystem'), ('Miscellaneous', 'Miscellaneous')], default='unspecified', max_length=50, null=True),
        ),
    ]
>>>>>>> deployment-backup
