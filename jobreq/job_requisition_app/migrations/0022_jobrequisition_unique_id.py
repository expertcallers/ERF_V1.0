# Generated by Django 3.2.9 on 2022-02-07 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_requisition_app', '0021_alter_jobrequisition_request_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobrequisition',
            name='unique_id',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]