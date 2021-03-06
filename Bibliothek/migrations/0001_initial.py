# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-26 01:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Altes_Buch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bezeichnung', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=30)),
                ('zeit_erstellt', models.DateTimeField(auto_now_add=True)),
                ('autor_und_titel', models.CharField(blank=True, max_length=255, null=True)),
                ('preis_kaufen', models.SmallIntegerField(blank=True, null=True)),
                ('anzahl_kaufen', models.SmallIntegerField(blank=True, default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Buch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bezeichnung', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=30)),
                ('zeit_erstellt', models.DateTimeField(auto_now_add=True)),
                ('titel', models.CharField(blank=True, max_length=255, null=True)),
                ('autor', models.CharField(blank=True, max_length=255, null=True)),
                ('isbn', models.CharField(blank=True, max_length=40, null=True)),
                ('adresse', models.CharField(blank=True, max_length=100, null=True)),
                ('ausgabe', models.CharField(blank=True, max_length=100, null=True)),
                ('herausgeber', models.CharField(blank=True, max_length=100, null=True)),
                ('serie', models.CharField(blank=True, max_length=100, null=True)),
                ('notiz', models.CharField(blank=True, max_length=100, null=True)),
                ('jahr', models.CharField(blank=True, max_length=4, null=True)),
                ('sprache', models.CharField(blank=True, max_length=3, null=True)),
                ('exlibris', models.CharField(blank=True, max_length=40, null=True)),
                ('stichworte', models.CharField(blank=True, max_length=255, null=True)),
                ('zusammenfassung', models.TextField(blank=True, null=True)),
                ('pdf', models.FileField(blank=True, null=True, upload_to='buecher')),
                ('epub', models.FileField(blank=True, null=True, upload_to='buecher')),
                ('mobi', models.FileField(blank=True, null=True, upload_to='buecher')),
                ('bild', models.ImageField(blank=True, null=True, upload_to='buecher')),
                ('alte_nr', models.SmallIntegerField(editable=False, null=True)),
                ('preis_kaufen', models.SmallIntegerField(blank=True, null=True)),
                ('anzahl_kaufen', models.SmallIntegerField(blank=True, default=0)),
                ('preis_leihen', models.SmallIntegerField(blank=True, null=True)),
                ('anzahl_leihen', models.SmallIntegerField(blank=True, default=0)),
                ('preis_druck', models.SmallIntegerField(blank=True, null=True)),
                ('anzahl_druck', models.SmallIntegerField(blank=True, default=0)),
                ('preis_pdf', models.SmallIntegerField(blank=True, null=True)),
                ('ob_pdf', models.BooleanField(default=0)),
                ('preis_mobi', models.SmallIntegerField(blank=True, null=True)),
                ('ob_mobi', models.BooleanField(default=0)),
                ('preis_epub', models.SmallIntegerField(blank=True, null=True)),
                ('ob_epub', models.BooleanField(default=0)),
            ],
            options={
                'verbose_name': 'Buch',
                'verbose_name_plural': 'Bücher',
            },
        ),
    ]
