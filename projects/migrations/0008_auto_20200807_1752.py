# Generated by Django 2.2.13 on 2020-08-07 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_auto_20200710_1943'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectpage',
            name='app_label',
            field=models.CharField(blank=True, choices=[('compressor', 'compressor'), ('joyous', 'joyous'), ('projects', 'projects'), ('standard', 'standard'), ('drp', 'drp'), ('mlp', 'mlp'), ('hrp', 'hrp'), ('lgrp', 'lgrp'), ('eppe', 'eppe'), ('gdb', 'gdb'), ('omo_mursi', 'omo_mursi'), ('origins', 'origins'), ('cc', 'cc'), ('fc', 'fc'), ('wtap', 'wtap'), ('publications', 'publications')], max_length=100, null=True),
        ),
    ]
