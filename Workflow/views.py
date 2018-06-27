import inspect
import csv
from datetime import datetime, date
from html2text import html2text
import sendgrid
import base64
import time

from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.forms.models import model_to_dict
from django.conf import settings

from Grundgeruest.models import ScholariumProfile
from .models import get_events, recipients_field_names, LegacyNewsletterAddress
from .forms import CSVForm, Newsletter, NewsletterForm
from . import utils


skripte_dir = "/home/scholarium/Skripte/"
python_bin = skripte_dir + "venv/bin/python3.6"


@staff_member_required
def control_view(request):
    if request.method == 'POST':
        return csv_export(request)

    menu = {
        'Rechnungen': reverse('Workflow:rechnungen'),
        # 'Newsletter senden (Achtung: E-Mail-Backend beachten)': reverse('Workflow:send_newsletter'),
        'Newsletter erstellen': reverse('Workflow:newsletter-list'),
    }

    csv_form = CSVForm()
    context = {
        'menu': menu,
        'csv_form': csv_form,
    }

    return render(request, 'Workflow/control-frame.html', context)


@staff_member_required
def skripte_view(request):
    if request.method == 'POST':
        method = getattr(utils, request.POST['function'])
        args = method.__defaults__
        if args:
            method(*args)
        else:
            method()

    # form = Rechnung2PdfForm
    # for f in inspect.getmembers(utils, inspect.isfunction):
    #     print(f)
    menu = {
        'Skripte': reverse('Workflow:skripte'),
        'Rechnungen': reverse('Workflow:rechnungen')
    }
    methods = {
        'Trello zu PDF': {
            'name': utils.trelloToSQL.__name__,
            'sig': inspect.signature(utils.trelloToSQL),  # Not used
            'doc': inspect.getdoc(utils.trelloToSQL),
        },
        'String drucken': {
            'name': utils.druck.__name__,
            'doc': inspect.getdoc(utils.druck),

        },
        'Veröffentlichen': {
            'name': utils.publish.__name__,
            'doc': inspect.getdoc(utils.publish)
        }
    }
    context = {
        'menu': menu,
        'methods': methods
    }

    return render(request, 'Workflow/skripte-view.html', context)


@staff_member_required
def rechnung_view(request):
    # CAUTION: currently no POST in control-frame, buttons were changed to links
    # to avoid a trailing "?" in the url due to an empty get request,
    # see commit
    if request.method == 'POST':
        pass  # TODO: import Rechnung2Pdf
    menu = {
        'Skripte': reverse('Workflow:skripte'),
        'Rechnungen': reverse('Workflow:rechnungen'),
    }
    # form = Rechnung2PdfForm

    context = {
        # 'form': form
        'menu': menu
    }
    return render(request, 'Workflow/rechnung-view.html', context)


@staff_member_required
def csv_export(request):
    """
    Generates csv-files with selected filters. (i.e. for manual import to Sendgrid)
    """
    values = request.POST.getlist('values')
    stufen = request.POST.getlist('stufen')
    states = request.POST.getlist('states')

    formatted_date = datetime.now().strftime('%d-%m-%Y_%H-%M')
    csv_filename = '{0}_{1}_{2}_{3}.csv'.format('+'.join(stufen),
                                                formatted_date,
                                                '+'.join(values),
                                                '+'.join(states))

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = \
        'attachment; filename="{}"'.format(csv_filename)

    writer = csv.writer(response)

    profiles = ScholariumProfile.objects.all()  # Not using Queryset filtering because of model functions.

    profile_list = []
    for profile in profiles:
        # Filter for seleceted tier
        if profile.get_stufe():
            print(profile.get_stufe().pk)
        stufe = profile.get_stufe().pk if profile.get_stufe() else 0
        if stufe not in [int(x) for x in stufen]:
            continue

        # Filter for aktiv/abgelaufen if existent
        ablauf = profile.get_ablauf()
        if ablauf:
            if 'abgelaufen' not in states and ablauf < date.today():
                continue
            if 'aktiv' not in states and ablauf >= date.today():
                continue

        profile_list.append(profile)

    # Split Nutzer values from Scholariumprofil values, because getattr() can't handle nested values
    user_values = []
    profile_values = []

    for i in values:
        if i in ['first_name', 'last_name', 'email']:
            user_values.append(i)
        else:
            profile_values.append(i)

    writer.writerow(user_values + profile_values)  # header-row
    for profile in profile_list:
        writer.writerow([getattr(profile.user, value) for value in user_values] + [getattr(profile, value) for value in profile_values])

    return response


# @staff_member_required
# def send_newsletter(request):
#     subject = 'Test Rundbrief'
#     body_html = (
#         '<p>Guten Tag,</p>'
#         '<p>dies ist ein Test.</p>'
#         '<p>Herzliche Grüße,'
#         '<br>Ihr scholarium</p>'
#     )
#     body_plain = html2text(body_html)
#     sender_address = 'scholarium <gk@scholarium.at>'
#     recipients = ScholariumProfile.objects.filter(newsletter=True)
#     reply_address = ['gk@scholarium.at']
#
#     messages = []
#
#     for recipient in recipients:
#         recipient_address = [recipient.user.email]
#         msg = EmailMultiAlternatives(
#             subject, body_plain, from_email=sender_address, to=recipient_address,
#             reply_to=reply_address
#         )
#         msg.attach_alternative(body_html, "text/html")
#         messages.append(msg)
#
#     connection = get_connection()
#     connection.send_messages(messages)
#
#     return HttpResponse(
#         "Der Newsletter wurde %s mal verschickt." % len(recipients)
#     )


@method_decorator(staff_member_required, name='dispatch')
class NewsletterList(ListView):
    model = Newsletter

    ordering = ['-id']


@method_decorator(staff_member_required, name='dispatch')
class NewsletterDetail(DetailView):
    model = Newsletter
    template_name = 'Workflow/newsletter_detail.html'

    # pass a dict with the verbose names and the Boolean values of the
    # recipients fields (e.g. recipients_gast) to be able to loop over it in the
    # template
    def get_context_data(self, **kwargs):
        context = super(NewsletterDetail, self).get_context_data(**kwargs)
        recipients_verbose_names = [
            Newsletter._meta.get_field(field).verbose_name for field in recipients_field_names
        ]
        recipients_values = [getattr(self.object, name) for name in recipients_field_names]
        recipients_dict = dict(zip(recipients_verbose_names, recipients_values))
        context['recipients_dict'] = recipients_dict
        return context


@method_decorator(staff_member_required, name='dispatch')
class NewsletterCreate(CreateView):
    model = Newsletter
    form_class = NewsletterForm

    def get_initial(self):
        """Prepopulate the form with the values of the Newsletter object which
        was chosen as a template in NewsletterList.
        """
        try:
            nl_obj = Newsletter.objects.get(slug=self.kwargs.get('slug'))
            # Only pass those fields which are defined in NewsletterForm;
            # Exclude events so all available events are checkmarked (which is
            # the model field default value) and not only those of nl_obj
            initial_data = model_to_dict(nl_obj, fields=NewsletterForm._meta.fields, exclude='events')
        except Newsletter.DoesNotExist:
            initial_data = {}

        return initial_data

    def get_success_url(self):
        """Redirect to NewsletterDetail with slug of the created newsletter
        object as argument.
        """
        return reverse('Workflow:newsletter-detail', kwargs={'slug': self.object.slug})


@method_decorator(staff_member_required, name='dispatch')
class NewsletterUpdate(UpdateView):
    model = Newsletter
    form_class = NewsletterForm

    def get_success_url(self):
        return reverse('Workflow:newsletter-detail', kwargs={'slug': self.kwargs.get('slug')})


@method_decorator(staff_member_required, name='dispatch')
class NewsletterDelete(DeleteView):
    model = Newsletter
    success_url = reverse_lazy('Workflow:index')
    success_message = 'Der Newsletter wurde verworfen.'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(NewsletterDelete, self).delete(request, *args, **kwargs)


@staff_member_required
def confirm_newsletter(request, slug):
    nl_obj = get_object_or_404(Newsletter, slug=slug)

    if request.method == 'POST':
        nl_obj = Newsletter.objects.get(slug=slug)
        nl_obj.confirmed = True
        nl_obj.save(update_fields=['confirmed'])
        messages.success(request, 'Der Newsletter wurde erfolgreich gespeichert.')
        # post_new_nl_to_sendgrid(nl_obj)
        return redirect('Workflow:index')
    else:
        return redirect('Workflow:newsletter-detail', slug=nl_obj.slug)


def post_new_nl_to_sendgrid(newsletter):
    """Sends the data from the newly created newsletter object to SendGrid.

    Receives newsletter object.
    """
    sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)

    # Create a new contact list for the new newsletter, name it like Bezeichnung.
    # TODO: Evaluate if it's better to update existing lists instead of always
    # creating a new one.
    contact_list_data = {
        "name": newsletter.bezeichnung
    }
    response = sg.client.contactdb.lists.post(request_body=contact_list_data)
    print(response.status_code)
    print(response.body)
    print(response.headers)
    # Get list_id from response to later identify the list the recipients will
    # be added to.
    list_id = response.to_dict['id']

    # First the recipients are added to SendGrid; SendGrid recognizes duplicates,
    # i.e., does not create a new entry for already existing addresses.
    # Then these recipients are identified by their recipient_id, which is the
    # base64-encoded email address, and added to the above created list which is
    # identified by its list_id.
    recipients = get_newsletter_recipients(newsletter)
    # Create a list with SendGrid's recipient_ids of the respective recipient.
    recipient_ids = []
    for rec in recipients:
        # encode() below converts the mail address from str to bytes so it can
        # be base64-encoded.
        # decode() converts the resulting base64 code from bytes to str so it
        # can be sent to SendGrid.
        recipient_ids.append(base64.urlsafe_b64encode(rec['email'].encode()).decode())
    # SendGrid is limited to 3 requests per second; recipients may be uploaded
    # in batches of 1000 per request. The rate at which recipients may be added
    # to a list is limited to 1 request per second.
    # Because len(recipients) == len(recipient_ids), the batch sizes are also
    # equal of equal length.
    if len(recipients) >= 1000:
        for i in range(len(recipients) // 1000):
            sg.client.contactdb.recipients.post(request_body=recipients[i*1000:(i+1)*1000])
            time.sleep(1)  # Play safe and wait 1 sec.
            sg.client.contactdb.lists._(list_id).recipients.post(request_body=recipient_ids[i*1000:(i+1)*1000])
            time.sleep(1)
    if len(recipients) % 1000 != 0:
        sg.client.contactdb.recipients.post(request_body=recipients[(len(recipients)//1000)*1000:])
        time.sleep(1)
        sg.client.contactdb.lists._(list_id).recipients.post(request_body=recipient_ids[(len(recipient_ids)//1000)*1000:])


def get_newsletter_recipients(newsletter):
    """Returns a list of dicts of all recipients of the newsletter."""
    profiles = ScholariumProfile.objects.filter(newsletter=True)
    recipient_groups = []
    recipients = []
    for field in recipients_field_names:
        if getattr(newsletter, field):
            recipient_groups.append(field[11:].capitalize())
    # add all legacy addresses to list recipients if True in newsletter
    if 'Legacy_addresses' in recipient_groups:
        legacy_addrs = LegacyNewsletterAddress.objects.all()
        for addr in legacy_addrs:
            recipients.append(dict(email=addr.email))
        # Remove Legacy_addresses because they are no longer needed
        recipient_groups.remove('Legacy_addresses')
    # convert the status-fields to ints so they can serve as check values later
    recipient_groups = [int(r[-1]) if r.startswith('Status') else r for r in recipient_groups]
    # if one of the following two cases is fulfilled,
    # the profile data (in dict form) will be added to recipients:
    # (I) supporter (profile.get_stufe()): then stufe and status of
    # the profile must be in recipient_groups;
    # (II) no supporter (not profile.get_stufe()): only the status
    # matters (which is O or 1) and must be in recipient_groups
    for profile in profiles:
        if ((profile.get_stufe()
                and profile.get_stufe().bezeichnung in recipient_groups
                and profile.get_Status()[0] in recipient_groups)
            or (not profile.get_stufe()
                and profile.get_Status()[0] in recipient_groups)):
            # After the long if-condition, add the recipients data to recipients.
            recipients.append(
                dict(
                    email=profile.user.email,
                    first_name=profile.user.first_name,
                    last_name=profile.user.last_name,
                    anrede=profile.anrede
                )
            )
    return recipients
