from django.contrib import admin

from .models import Newsletter, recipients_field_names, LegacyNewsletterAddress


class NewsletterAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['bezeichnung', 'slug', 'subject']}),
        ('Empfängergruppen', {'fields': [rec_field for rec_field in recipients_field_names]}),
        (None, {'fields': ['sent_to']}),
        ('Anrede', {'fields': ['salutation', 'default_salutation']}),
        ('Inhalt', {'fields': ['body_template', 'preheader', 'text']}),
        ('Veranstaltungen', {'fields': [
            'events', 'events_template',
        ]}),
        ('Rest', {'fields': [
            'html_content', 'plain_content', 'status', 'send_date',
            'sender_id', 'custom_unsubscribe_url', 'confirmed'
        ]}),
    ]


class LegacyNewsletterAddressAdmin(admin.ModelAdmin):
    model = LegacyNewsletterAddress
    search_fields = ['email']


admin.site.register(Newsletter, NewsletterAdmin)
admin.site.register(LegacyNewsletterAddress, LegacyNewsletterAddressAdmin)
