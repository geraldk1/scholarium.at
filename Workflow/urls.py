from django.conf.urls import url

from .views import (
    control_view, skripte_view, rechnung_view,  # send_newsletter,
    NewsletterList, NewsletterCreate, NewsletterUpdate, NewsletterDetail, NewsletterDelete, confirm_newsletter,
)

app_name = 'Workflow'

urlpatterns = [
    url('^skripte/$', skripte_view, name='skripte'),
    url('^rechnungen/$', rechnung_view, name='rechnungen'),
    # url(r'^newsletter-verschicken/$', send_newsletter, name='send_newsletter'),
    url(
        r'^newsletter/vorlagen/$',
        NewsletterList.as_view(),
        name='newsletter-list'
    ),
    url(
        r'^newsletter/erstellen/$',
        NewsletterCreate.as_view(),
        name='newsletter-create'
    ),
    url(
        r'^newsletter/erstellen/vorlage/(?P<slug>[-\w]+)/$',
        NewsletterCreate.as_view(),
        name='newsletter-create-with-template'
    ),
    url(
        r'^newsletter/vorschau/(?P<slug>[-\w]+)/$',
        NewsletterDetail.as_view(),
        name='newsletter-detail',
    ),
    url(
        r'^newsletter/bearbeiten/(?P<slug>[-\w]+)/$',
        NewsletterUpdate.as_view(),
        name='newsletter-update',
    ),
    url(
        r'^newsletter/verwerfen/(?P<slug>[-\w]+)/$',
        (NewsletterDelete.as_view()),
        name='newsletter-delete',
    ),
    url(
        r'^newsletter/gespeichert/(?P<slug>[-\w]+)/$',
        confirm_newsletter,
        name='newsletter-confirm',
    ),
    url(r'^$', control_view, name='index'),
]
