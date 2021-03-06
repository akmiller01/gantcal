# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-04 20:08
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cal', '0026_auto_20160304_1955'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attachment',
            options={'ordering': ['modified', 'title']},
        ),
        migrations.AddField(
            model_name='attachment',
            name='modified',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2016, 3, 4, 20, 8, 8, 987880, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='attachment',
            name='modifier',
            field=models.ForeignKey(default=3, editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='modified_attachment', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
