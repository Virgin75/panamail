# Generated by Django 4.2 on 2023-06-03 14:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AutomationCampaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=89)),
                ('description', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('DRAFT', 'Automation campaign is in Draft.'), (
                'ACTIVE', 'Automation campaign is active and emails are being sent.'),
                                                     ('PAUSED', 'Automation campaign is stopped.')], default='DRAFT',
                                            max_length=15)),
                ('trigger_type', models.CharField(blank=True,
                                                  choices=[('EVENT', 'Event trigger'), ('PAGE', 'Page trigger'),
                                                           ('EMAIL', 'Email trigger'), ('LIST', 'List trigger'),
                                                           ('SEGMENT', 'Segment trigger'), ('TIME', 'Time trigger')],
                                                  max_length=15, null=True)),
                ('is_repeated', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AutomationCampaignContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.IntegerField(default=0)),
                ('step_type', models.CharField(
                    choices=[('SEND_EMAIL', 'Send an email when the Contact enters this Step.'),
                             ('WAIT', 'Wait for a specific time before processing the next Step.')],
                    default='SEND_EMAIL', max_length=50)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='StepSendEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StepWait',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('delay', models.IntegerField(default=1)),
                ('delay_unit', models.CharField(
                    choices=[('days', 'Day'), ('hours', 'Hour'), ('weeks', 'Week'), ('minutes', 'Minute')],
                    default='days', max_length=15)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TriggerEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('action', models.CharField(blank=True,
                                            choices=[('SENT', 'The email was sent'), ('OPEN', 'The email was open'),
                                                     ('CLICK', 'The email was clicked'),
                                                     ('UNSUB', 'The contact unsubscribed from the list'),
                                                     ('SPAM', 'The contact marked the campaign as spam'),
                                                     ('BOUNC', 'The email bounced')], max_length=50, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TriggerEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=50)),
                ('with_attributes', models.JSONField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TriggerList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TriggerPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TriggerSegment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TriggerTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('unit', models.CharField(blank=True, choices=[('DAY', 'Day'), ('WEEK', 'Week'), ('MONTH', 'Month'),
                                                               ('YEAR', 'Year')], max_length=50, null=True)),
                ('value', models.IntegerField(blank=True, default=1, null=True)),
                ('rq_cron_job_id', models.CharField(blank=True, max_length=50, null=True)),
                ('automation_campaign',
                 models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                      related_name='time_trigger', to='automation.automationcampaign')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
