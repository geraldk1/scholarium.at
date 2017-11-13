# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-26 15:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Veranstaltungen', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artderveranstaltung',
            name='slug',
            field=models.SlugField(blank=True, max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='studiumdings',
            name='slug',
            field=models.SlugField(blank=True, max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='veranstaltung',
            name='slug',
            field=models.SlugField(blank=True, max_length=30, unique=True),
        ),
    ]