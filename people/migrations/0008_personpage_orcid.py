# Generated by Django 2.2.13 on 2020-07-27 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0007_personpage_state_province'),
    ]

    operations = [
        migrations.AddField(
            model_name='personpage',
            name='orcid',
            field=models.URLField(blank=True, null=True),
        ),
    ]
