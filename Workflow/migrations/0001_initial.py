# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-06-27 13:59
from __future__ import unicode_literals

import Workflow.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Veranstaltungen', '0005_auto_20171106_1407'),
    ]

    operations = [
        migrations.CreateModel(
            name='LegacyNewsletterAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
            ],
            options={
                'verbose_name': 'E-Mail-Adresse',
                'verbose_name_plural': 'Newsletter-Adressen (nicht in Nutzerprofile)',
                'ordering': ('email',),
            },
        ),
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bezeichnung', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
                ('zeit_erstellt', models.DateTimeField(auto_now_add=True)),
                ('subject', models.CharField(max_length=200, verbose_name='Betreff')),
                ('sent_to', models.TextField(blank=True, null=True, verbose_name='Gesendet an folgende Adressen')),
                ('preheader', models.TextField()),
                ('salutation', models.CharField(choices=[('LIEBER', 'Liebe/r Frau/Herr'), ('GEEHRTER', 'Sehr geehrte/r Frau/Herr'), ('ANDERE_ANREDE', 'Andere Anrede')], default='LIEBER', help_text='Die ersten beiden Optionen werden personalisiert. Falls keine Personalisierung möglich ist, wird die Anrede im unteren Textfeld herangezogen. Bei Option "Andere Anrede" bekommt jeder Empfänger die Anrede im unteren Textfeld, unabhängig davon, ob eine personalisierte Anrede möglich ist oder nicht.', max_length=100, verbose_name='Anredemöglichkeiten')),
                ('default_salutation', models.CharField(default='Liebe Unterstützer und Interessierte', help_text='Bitte hier die Default-Anrede für obige Optionen der personalisierten Anrede eintragen bzw. die Anrede für alle Empfänger, falls oben die Option "Andere Anrede" ausgewählt ist.', max_length=200, verbose_name='Default-Anrede')),
                ('text', models.TextField()),
                ('body_template', models.TextField(help_text='Gibt die Struktur des Newsletters vor. Preheader, Anrede, Text, Veranstaltungen werden anstelle der Platzhalter, z.B. [%preheader%], eingefügt.', verbose_name='Inhaltsvorlage')),
                ('events_template', models.TextField(blank=True, help_text='Der Inhalt dieser Vorlage wird anstelle von [%events%] in der Inhaltsvorlage eingesetzt, für jede Veranstaltung mit den jeweiligen Daten.', null=True, verbose_name='Vorlage Veranstaltungstext')),
                ('html_content', models.TextField(blank=True, help_text='Dieses Feld wird beim Speichern automatisch aus den jeweiligen Inhalten der anderen Felder befüllt und muss nicht bearbeitet werden. Es sei denn, der HTML-Text soll manuell eingetragen werden; in jenem Fall bitte die obige Checkbox anklicken und den HTML-Code hier eintragen/ändern.', null=True, verbose_name='Gesamter HTML-Text')),
                ('plain_content', models.TextField(blank=True, help_text='Das Klartext-Feld wird automatisch beim Speichern durch Umwandeln des HTML-Textes befüllt und muss nicht bearbeitet werden. Es sei denn, der Klartext soll manuell eingetragen werden; in jenem Fall bitte die obige Checkbox anklicken und den Klartext hier eintragen/ändern.', null=True, verbose_name='Gesamter Klartext')),
                ('status', models.CharField(choices=[('DRAFT', 'Entwurf'), ('SCHEDULED', 'Versandzeit festgelegt'), ('SENT', 'Verschickt')], default='DRAFT', max_length=50)),
                ('send_date', models.DateTimeField(blank=True, help_text='falls "Versandzeit festgelegt", Format z.B.: TT.MM.JJJJ hh:mm:ss. Wird der Status "Versandzeit festgelegt" gewählt und hier keine Zeit eingetragen, wird der Newsletter sofort nach der Erstellung verschickt.', null=True, verbose_name='Versandzeit')),
                ('sender_id', models.PositiveIntegerField()),
                ('custom_unsubscribe_url', models.URLField(blank=True, null=True)),
                ('confirmed', models.BooleanField(default=False, verbose_name='Bestätigt')),
                ('recipients_legacy_addresses', models.BooleanField(default=True, verbose_name='Sonstige Newsletter-Adressen von früher (die nicht in Nutzerprofile enthalten sind)')),
                ('recipients_gast', models.BooleanField(default=True, verbose_name='Gast')),
                ('recipients_teilnehmer', models.BooleanField(default=True, verbose_name='Teilnehmer')),
                ('recipients_scholar', models.BooleanField(default=True, verbose_name='Scholar')),
                ('recipients_partner', models.BooleanField(default=True, verbose_name='Partner')),
                ('recipients_beirat', models.BooleanField(default=True, verbose_name='Beirat')),
                ('recipients_patron', models.BooleanField(default=True, verbose_name='Patron')),
                ('recipients_status_0', models.BooleanField(default=True, verbose_name='Kein Unterstützer')),
                ('recipients_status_1', models.BooleanField(default=True, verbose_name='Abgelaufen')),
                ('recipients_status_2', models.BooleanField(default=True, verbose_name='30 Tage bis Ablauf')),
                ('recipients_status_3', models.BooleanField(default=True, verbose_name='Aktiv')),
                ('events', models.ManyToManyField(blank=True, default=Workflow.models.get_events, help_text='In obiger Auswahl sind nur zukünftige Veranstaltungen aufgeführt, die noch nicht ausgebucht sind.', to='Veranstaltungen.Veranstaltung', verbose_name='Am Ende des Newsletters aufzuführende Veranstaltungen')),
            ],
            options={
                'verbose_name_plural': 'Newsletter',
            },
        ),
    ]
