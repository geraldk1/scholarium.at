# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-25 00:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Veranstaltungen', '0014_auto_20171025_0037'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studiumdings',
            name='ob_buchung',
        ),
        migrations.AddField(
            model_name='studiumdings',
            name='anzahl_buchung',
            field=models.SmallIntegerField(blank=True, default=0),
        ),
    ]
