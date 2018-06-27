from datetime import date, datetime

from django.db import models
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError
from django.urls import reverse

from seite.models import Grundklasse
from Veranstaltungen.models import Veranstaltung
from Produkte.models import Spendenstufe
from Grundgeruest.models import ScholariumProfile


def get_events():
    """Create a callable to set the default value of the events field in
    class Newsletter to all available future events.
    """
    return Veranstaltung.objects.filter(datum__gte=date.today(), anzahl_teilnahme__gt=0)


class Newsletter(Grundklasse):
    LIEBER = 'LIEBER'
    GEEHRTER = 'GEEHRTER'
    ANDERE_ANREDE = 'ANDERE_ANREDE'
    SALUTATION_CHOICES = (
        (LIEBER, 'Liebe/r Frau/Herr'),
        (GEEHRTER, 'Sehr geehrte/r Frau/Herr'),
        (ANDERE_ANREDE, 'Andere Anrede')
    )
    DEFAULT_SALUTATION = 'Liebe Unterstützer und Interessierte'
    DRAFT_STATUS = 'DRAFT'
    SCHEDULED_STATUS = 'SCHEDULED'
    SENT_STATUS = 'SENT'
    STATUS_CHOICES = (
        (DRAFT_STATUS, 'Entwurf'),
        (SCHEDULED_STATUS, 'Versandzeit festgelegt'),
        (SENT_STATUS, 'Verschickt')
    )

    subject = models.CharField('Betreff', max_length=200)
    sent_to = models.TextField(
        'Gesendet an folgende Adressen', null=True, blank=True,
    )
    preheader = models.TextField()
    salutation = models.CharField(
        'Anredemöglichkeiten', max_length=100, choices=SALUTATION_CHOICES,
        default=LIEBER,
        help_text=(
            'Die ersten beiden Optionen werden '
            'personalisiert. Falls keine Personalisierung möglich ist, wird die '
            'Anrede im unteren Textfeld herangezogen. Bei Option "Andere Anrede" '
            'bekommt jeder Empfänger die Anrede im unteren Textfeld, unabhängig '
            'davon, ob eine personalisierte Anrede möglich ist oder nicht.'
        ),
    )
    default_salutation = models.CharField(
        'Default-Anrede', max_length=200, default=DEFAULT_SALUTATION,
        help_text=(
            'Bitte hier die Default-Anrede für obige Optionen der '
            'personalisierten Anrede eintragen bzw. die Anrede für alle '
            'Empfänger, falls oben die Option "Andere Anrede" ausgewählt ist.'
        ),
    )
    text = models.TextField()
    body_template = models.TextField(
        'Inhaltsvorlage',
        help_text=(
            'Gibt die Struktur des Newsletters vor. Preheader, Anrede, Text, '
            'Veranstaltungen werden anstelle der Platzhalter, z.B. [%preheader%],'
            ' eingefügt.'
        ),
    )
    events = models.ManyToManyField(
        Veranstaltung,
        limit_choices_to={
            'datum__gte': date.today(),
            'anzahl_teilnahme__gt': 0,
        },
        blank=True, default=get_events,
        verbose_name='Am Ende des Newsletters aufzuführende Veranstaltungen',
        help_text=(
            'In obiger Auswahl sind nur zukünftige Veranstaltungen aufgeführt, '
            'die noch nicht ausgebucht sind.'
        ),
    )
    events_template = models.TextField(
        'Vorlage Veranstaltungstext', null=True, blank=True,
        help_text=(
            'Der Inhalt dieser Vorlage wird anstelle von [%events%] in der '
            'Inhaltsvorlage eingesetzt, für jede Veranstaltung mit den '
            'jeweiligen Daten.'
        ),
    )
    html_content = models.TextField(
        'Gesamter HTML-Text', null=True, blank=True,
        help_text=(
            'Dieses Feld wird beim Speichern automatisch aus den jeweiligen '
            'Inhalten der anderen Felder befüllt und muss nicht bearbeitet '
            'werden. Es sei denn, der HTML-Text soll manuell eingetragen '
            'werden; in jenem Fall bitte die obige Checkbox anklicken und den '
            'HTML-Code hier eintragen/ändern.'
        ),
    )
    plain_content = models.TextField(
        'Gesamter Klartext', null=True, blank=True,
        help_text=(
            'Das Klartext-Feld wird automatisch beim Speichern durch Umwandeln '
            'des HTML-Textes befüllt und muss nicht bearbeitet werden. Es sei '
            'denn, der Klartext soll manuell eingetragen werden; in jenem Fall '
            'bitte die obige Checkbox anklicken und den Klartext hier '
            'eintragen/ändern.'
        ),
    )
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default=DRAFT_STATUS
    )
    send_date = models.DateTimeField(
        'Versandzeit', null=True, blank=True,
        help_text=(
            'falls "Versandzeit festgelegt", Format z.B.: TT.MM.JJJJ hh:mm:ss. '
            'Wird der Status "Versandzeit festgelegt" gewählt und hier keine '
            'Zeit eingetragen, wird der Newsletter sofort nach der Erstellung '
            'verschickt.'
        ),
    )
    sender_id = models.PositiveIntegerField()
    custom_unsubscribe_url = models.URLField(null=True, blank=True)
    confirmed = models.BooleanField('Bestätigt', default=False)
    recipients_legacy_addresses = models.BooleanField(
        'Sonstige Newsletter-Adressen von früher (die nicht in '
        'Nutzerprofile enthalten sind)', default=True
    )
    # the other recipients_options are added below with add_to_class()

    class Meta:
        verbose_name_plural = 'Newsletter'

    def get_absolute_url(self):
        return reverse('newsletter-detail', kwargs={'slug: self.slug'})

    def clean(self):
        error_dict = {}
        # Do not allow to use existing bezeichnung;
        # (self._state.adding is True) is there to not prevent updating an
        # existing Newsletter object
        if (Newsletter.objects.filter(slug=slugify(self.bezeichnung)).exists()
                and self._state.adding is True):
            error_dict['bezeichnung'] = ValidationError(
                'Es existiert bereits ein Newsletter mit dieser Bezeichnung '
                '(genauer: mit deren slug). Bitte die Bezeichnung ändern.'
            )
        # Do not allow send_dates which are in the past
        if self.send_date and self.send_date.date() < datetime.today().date():
            error_dict['send_date'] = ValidationError(
                'Der Versandtag liegt in der Vergangenheit.'
            )
        # Do not allow drafts with a send_date
        if self.status == Newsletter.DRAFT_STATUS and self.send_date is not None:
            error_dict['send_date'] = ValidationError(
                'Bitte bei Entwürfen keine Versandzeit eintragen.'
            )
        if error_dict:
            raise ValidationError(error_dict)
        # set send_date to now for scheduled newsletters if no date is given
        if self.status == Newsletter.SCHEDULED_STATUS and self.send_date is None:
            self.send_date = datetime.now()


# To keep it DRY, the remaining model fields for filtering the recipients
# (Spendenstufe and PROFILE_STATUS_OPTIONS) are added here with add_to_class.
spendenstufen = [s.bezeichnung for s in Spendenstufe.objects.all()]
profile_status = [s for s in ScholariumProfile.PROFILE_STATUS_OPTIONS]

# create list of field names starting with recipients_* for easier access
# elsewhere (e.g. in admin.py or forms.py)
recipients_field_names = []

for spendenstufe in spendenstufen:
    field_name_stufe = 'recipients_' + spendenstufe.lower()
    recipients_field_names.append(field_name_stufe)

    Newsletter.add_to_class(
        field_name_stufe,
        models.BooleanField(spendenstufe, default=True),
    )

for pr_status in profile_status:
    field_name_status = 'recipients_status_' + str(pr_status[0])
    recipients_field_names.append(field_name_status)

    Newsletter.add_to_class(
        field_name_status,
        models.BooleanField(pr_status[1], default=True),
    )

recipients_field_names.append('recipients_legacy_addresses')


class LegacyNewsletterAddress(models.Model):
    email = models.EmailField()

    class Meta:
        verbose_name = 'E-Mail-Adresse'
        verbose_name_plural = 'Newsletter-Adressen (nicht in Nutzerprofile)'
        ordering = ('email',)

    def __str__(self):
        return self.email
