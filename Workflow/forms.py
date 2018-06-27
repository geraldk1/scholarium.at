import pypandoc
from html2text import html2text

from django import forms

from Produkte.models import Spendenstufe
from .models import get_events, Newsletter, recipients_field_names


class Rechnung2PdfForm(forms.Form):
    firm = forms.CharField(max_length=50, initial='scholarium')
    author = forms.CharField(max_length=50, initial='Georg A. Schabetsberger')
    recipent = forms.CharField(initial='''Max Mustermann
Holsteinische Str. 777
10717 Berlin
Deutschland''', widget=forms.Textarea)
    # ansprache = forms.CharField(initial='')
    # startnote = forms.CharField(initial='')

    description = forms.CharField(max_length=100, label='description')
    count = forms.IntegerField(label='count')
    price = forms.FloatField(label='price')
    details = forms.CharField(label='details')

    middlenote = forms.CharField(initial='Bitte überweisen Sie den Gesamtbetrag innerhalb von 14 Tagen, mit Angabe '
                                         'der Rechnungsnummer, auf folgendes Konto:',
                                 widget=forms.Textarea)

    Inhaber = forms.CharField(max_length=100, label='Inhaber', initial='scholarium')
    IBAN = forms.CharField(max_length=100, label='IBAN', initial='AT81 2011 1827 1589 8503')
    BIC = forms.CharField(max_length=100, label='BIC', initial='GIBAATWWXXX')

    # closingnote = forms.CharField(initial = 'Mit freundlichen Grüßen,')


class TrelloToSQLForm():
    pass


class CSVForm(forms.Form):
    fields = [
        ('anrede', 'Anrede'),
        ('first_name', 'Vorname'),
        ('last_name', 'Nachname'),
        ('email', 'Email'),
        ('strasse', 'Straße'),
        ('ort', 'Ort'),
        ('land', 'Land'),
        ('firma', 'Firma'),
        ('plz', 'Postleitzahl'),
        ('datum_ablauf', 'Ablaufsdatum')
    ]
    state_fields = [
        ('abgelaufen', 'abgelaufen'),
        ('aktiv', 'aktiv'),
    ]
    stufe_choices = [('0', 'Interessent')] + [(s.pk, s.bezeichnung) for s in Spendenstufe.objects.all()]

    values = forms.MultipleChoiceField(fields, widget=forms.CheckboxSelectMultiple)
    stufen = forms.MultipleChoiceField(stufe_choices, widget=forms.CheckboxSelectMultiple)
    states = forms.MultipleChoiceField(state_fields, widget=forms.CheckboxSelectMultiple)


def get_status_choices_without_sent():
    """Remove (SENT_STATUS, 'Verschickt') from the displayed status choices"""
    limited_status_choices = list(Newsletter.STATUS_CHOICES)
    # except-pass to cause no error if the choice is not available to be removed
    try:
        limited_status_choices.remove((Newsletter.SENT_STATUS, 'Verschickt'))
    except ValueError:
        pass
    return limited_status_choices


class NewsletterForm(forms.ModelForm):
    # initialize get_status_choices_without_sent to not display the status
    # option (SENT_STATUS, 'Verschickt')
    def __init__(self, *args, **kwargs):
        super(NewsletterForm, self).__init__(*args, **kwargs)
        self.fields['status'] = forms.ChoiceField(
            choices=get_status_choices_without_sent()
        )
        # order available events by 'datum'
        self.fields['events'].queryset = get_events().order_by('datum')

    edit_html = forms.BooleanField(
        label='HTML-Text manuell eingeben', required=False,
        help_text=(
            'Bitte nur anklicken, wenn der gesamte HTML-Text manuell in der '
            'folgenden Textbox eingetragen wird und nicht automatisch aus den '
            'Einträgen der vorherigen Felder erzeugt werden soll.'
        ),
    )
    edit_plain = forms.BooleanField(
        label='Klartext manuell eingeben', required=False,
        help_text=(
            'Bitte nur anklicken, wenn der Klartext manuell in der folgenden '
            'Textbox eingetragen wird und nicht automatisch aus dem HTML-Text '
            'erzeugt werden soll.'
        ),
    )

    class Meta:
        model = Newsletter
        fields = [
            'bezeichnung', 'subject', 'preheader', 'salutation',
            'default_salutation', 'body_template', 'text', 'events',
            'events_template', 'body_template', 'edit_html', 'html_content', 'edit_plain', 'plain_content',
            'status', 'send_date', 'sender_id', 'custom_unsubscribe_url',
        ]
        # add recipient_fields to fields at the position after 'subject'
        for num, rec_field in enumerate(recipients_field_names, start=2):
            fields.insert(num, rec_field)

        INPUT_COLS = 80
        INPUT_ROWS = 10

        widgets = {
            'events': forms.CheckboxSelectMultiple(),
            'preheader': forms.TextInput(attrs={'size': INPUT_COLS}),
            'default_salutation': forms.TextInput(attrs={'size': INPUT_COLS}),
            'body_template': forms.Textarea(attrs={'cols': INPUT_COLS, 'rows': INPUT_ROWS}),
            'text': forms.Textarea(attrs={'cols': INPUT_COLS, 'rows': INPUT_ROWS}),
            'events_template': forms.Textarea(attrs={'cols': INPUT_COLS, 'rows': INPUT_ROWS}),
            'html_content': forms.Textarea(attrs={'cols': INPUT_COLS, 'rows': INPUT_ROWS}),
            'plain_content': forms.Textarea(attrs={'cols': INPUT_COLS, 'rows': INPUT_ROWS}),
        }
        help_texts = {
            'bezeichnung':
                'Titel des Datenbankeintrags; sollte eindeutig sein. Die '
                'Bezeichnung taucht nicht im verschickten Newsletter auf.',
            'edit_html':
                'Anklicken, wenn der HTML-Text manuell eingetragen und nicht '
                'automatisch aus den anderen Feldern erzeugt werden soll.',
            'edit_plain':
                'Anklicken, wenn der Klartext manuell eingetragen und nicht '
                'automatisch aus dem HTML-Text erzeugt werden soll.',
        }

    def save(self):
        """Create the html and plain content of the Newsletter
        by converting the user input from markdown to html as well as creating
        the content for the selected events in the form; if there is no opt-out
        by checking edit_html or edit_plain, in that case the manual entries in
        the html_content or plain_content fields are saved to the database
        """
        # the form is saved here for the first time to be able to use the
        # events queryset (ManytoManyField); otherwise when calling
        # new_nl.events.all().exists(), the following error is raised:
        # ValueError: “needs to have a value for field ”id“ before this
        # many-to-many relationship can be used”);
        # there may be better ways to handle this.
        new_nl = super(NewsletterForm, self).save()

        if not self.cleaned_data.get('edit_html'):
            wochentage = (
                'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag',
                'Samstag', 'Sonntag',
            )
            events_content = ''
            if new_nl.events.all().exists():
                for event in new_nl.events.all().order_by('datum'):
                    # Alternatively, "scholarium.at" below, i.e. the domain, in the
                    # following string could be retrieved with:
                    # from django.contrib.sites.models import Site
                    # Site.objects.get_current().domain
                    event_title = (
                        '<a href="https://scholarium.at{0}">{1}: {2} ({3}, {4}.{5}.)</a>'
                        .format(
                            event.get_absolute_url(), event.art_veranstaltung,
                            event.bezeichnung, wochentage[event.datum.weekday()],
                            event.datum.day, event.datum.month,
                        )
                    )
                    event_content = (
                        new_nl.events_template.replace('[%event_title%]', event_title, 1)
                                              .replace('[%event_text%]', event.beschreibung, 1)
                    )
                    events_content += event_content
            # convert relevant entries from markdown to html
            md_vars = [new_nl.preheader, new_nl.text]
            preheader, text = [
                pypandoc.convert_text(m, 'html', format='md', encoding='utf-8') for m in md_vars
            ]
            # substitute the placeholders within these brackets [%...%]
            # in the body_template with the respective form entries
            new_nl.html_content = (
                new_nl.body_template.replace('[%preheader%]', preheader, 1)
                                    .replace('[%salutation%]', new_nl.default_salutation, 1)
                                    .replace('[%text%]', text, 1)
                                    .replace('[%events%]', events_content, 1)
            )
        if not self.cleaned_data.get('edit_plain'):
            # convert html-mail to plain text with html2text;
            # the replace-tweaks are remove the |-signs which are created from
            # html2text from the table-tags in the html_content
            # maybe this can be solved in the body_template field;
            # if so the replaces should be removed
            new_nl.plain_content = (
                html2text(new_nl.html_content).replace('|  |  |  |\n\n', '')
                                              .replace('|  |\n', '')
                                              .replace('\n| ', '\n')
                                              .replace('\n|\n', '\n')
            )
        new_nl.save()
        return new_nl
