# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-09 14:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0027_auto_20160304_2008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='title',
            field=models.CharField(max_length=2000),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_URL',
            field=models.URLField(blank=True, max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='title',
            field=models.CharField(max_length=2000),
        ),
    ]
