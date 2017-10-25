# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-10-03 16:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bibliothek', '0006_auto_20171002_1052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buch',
            name='bild',
            field=models.ImageField(blank=True, null=True, upload_to='buecher'),
        ),
        migrations.AlterField(
            model_name='buch',
            name='epub',
            field=models.FileField(blank=True, null=True, upload_to='buecher'),
        ),
        migrations.AlterField(
            model_name='buch',
            name='mobi',
            field=models.FileField(blank=True, null=True, upload_to='buecher'),
        ),
        migrations.AlterField(
            model_name='buch',
            name='pdf',
            field=models.FileField(blank=True, null=True, upload_to='buecher'),
        ),
    ]