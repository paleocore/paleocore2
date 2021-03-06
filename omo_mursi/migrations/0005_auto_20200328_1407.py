# Generated by Django 2.2.5 on 2020-03-28 14:07

import ckeditor.fields
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('omo_mursi', '0004_auto_20200328_1404'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='identificationqualifier',
            options={'verbose_name': '07-MLP ID Qualifier'},
        ),
        migrations.AddField(
            model_name='identificationqualifier',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was first created.', verbose_name='Created'),
        ),
        migrations.AddField(
            model_name='identificationqualifier',
            name='date_last_modified',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was last altered.', verbose_name='Modified'),
        ),
        migrations.AddField(
            model_name='identificationqualifier',
            name='last_import',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='identificationqualifier',
            name='problem',
            field=models.BooleanField(default=False, help_text='Is there a problem with this record that needs attention?'),
        ),
        migrations.AddField(
            model_name='identificationqualifier',
            name='problem_comment',
            field=models.TextField(blank=True, help_text='Description of the problem.', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='identificationqualifier',
            name='remarks',
            field=ckeditor.fields.RichTextField(blank=True, help_text='General remarks about this database record.', null=True, verbose_name='Record Remarks'),
        ),
        migrations.AlterField(
            model_name='identificationqualifier',
            name='qualified',
            field=models.BooleanField(default=False),
        ),
    ]
