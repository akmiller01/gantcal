# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-29 15:21
from __future__ import unicode_literals

import cal.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0020_auto_20160226_1441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='attendees_approved',
            field=cal.models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='event',
            name='date_confirmed',
            field=cal.models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='objectives_approved',
            field=cal.models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='task',
            name='endIsMilestone',
            field=cal.models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='task',
            name='hasChild',
            field=cal.models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='task',
            name='startIsMilestone',
            field=cal.models.BooleanField(default=False),
        ),
    ]
