# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-21 12:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0030_auto_20160316_1222'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cross_Cutting_Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, unique=True)),
                ('slug', models.SlugField(editable=False, max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('start', models.DateField(blank=True, null=True)),
                ('end', models.DateField()),
                ('theme', models.ManyToManyField(blank=True, related_name='cross_cutting_areas', related_query_name='cross_cutting_area', to='cal.Theme')),
            ],
            options={
                'ordering': ['start', 'title'],
                'verbose_name_plural': 'cross cutting areas',
            },
        ),
        migrations.RemoveField(
            model_name='process',
            name='theme',
        ),
        migrations.RemoveField(
            model_name='event',
            name='process',
        ),
        migrations.DeleteModel(
            name='Process',
        ),
        migrations.AddField(
            model_name='event',
            name='cross_cutting_area',
            field=models.ManyToManyField(blank=True, related_name='events', related_query_name='event', to='cal.Cross_Cutting_Area'),
        ),
    ]
