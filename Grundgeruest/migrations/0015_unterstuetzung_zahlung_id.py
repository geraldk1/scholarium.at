# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-05-06 20:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Grundgeruest', '0014_auto_20180504_1518'),
    ]

    operations = [
        migrations.AddField(
            model_name='unterstuetzung',
            name='zahlung_id',
            field=models.CharField(blank=True, max_length=200, null=True, unique=True),
        ),
    ]
