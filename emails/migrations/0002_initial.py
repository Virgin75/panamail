# Generated by Django 4.0 on 2023-04-01 19:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('emails', '0001_initial'),
        ('commons', '0002_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='senderemail',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_set', to='users.customuser'),
        ),
        migrations.AddField(
            model_name='senderemail',
            name='domain',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='emails.senderdomain'),
        ),
        migrations.AddField(
            model_name='senderemail',
            name='edit_history',
            field=models.ManyToManyField(blank=True, to='commons.History'),
        ),
        migrations.AddField(
            model_name='senderemail',
            name='workspace',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.workspace'),
        ),
        migrations.AddField(
            model_name='senderdomain',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_set', to='users.customuser'),
        ),
        migrations.AddField(
            model_name='senderdomain',
            name='edit_history',
            field=models.ManyToManyField(blank=True, to='commons.History'),
        ),
        migrations.AddField(
            model_name='senderdomain',
            name='workspace',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.workspace'),
        ),
        migrations.AddField(
            model_name='email',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_set', to='users.customuser'),
        ),
        migrations.AddField(
            model_name='email',
            name='edit_history',
            field=models.ManyToManyField(blank=True, to='commons.History'),
        ),
        migrations.AddField(
            model_name='email',
            name='tags',
            field=models.ManyToManyField(blank=True, to='commons.Tag'),
        ),
        migrations.AddField(
            model_name='email',
            name='workspace',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.workspace'),
        ),
    ]