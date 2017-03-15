""" URL Configuration der scholarium-Seite

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from Grundgeruest.views import TemplateMitMenue, ListeMitMenue, aus_datei_mitglieder_einlesen, db_runterladen
from Grundgeruest.forms import Anmeldeformular
from userena.views import signup
from Veranstaltungen.urls import *
from Veranstaltungen.models import Studiumdings
from Produkte.models import Spendenstufen

urlpatterns = [
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^fragen/',
        TemplateMitMenue.as_view(
            template_name='Gast/fragen.html'),
        name='gast_fragen'),
    url(r'^studium/$', 
        ListeMitMenue.as_view(
            model=Studiumdings,
    	    template_name='Veranstaltungen/liste_studien.html',
	        context_object_name = 'studien'
        ),
        name='liste_gast_studium'),
    url(r'^studium/(?P<slug>[-\w]+)/$',
        DetailMitMenue.as_view(
            template_name='Veranstaltungen/detail.html',
            model=Studiumdings,
            context_object_name = 'veranstaltung'),
        name='studium_gast_detail'),
    url(r'^vortrag/',
        TemplateMitMenue.as_view(
            template_name='Gast/vortrag.html'),
        name='gast_vortrag'),
    url(r'^accounts/signup/$',
        signup,
        {'signup_form': Anmeldeformular}),
    url(r'^accounts/e$',
        aus_datei_mitglieder_einlesen,
        name='mitglieder_einlesen'),
    url(r'^accounts/', include('userena.urls')),
    url(r'^warenkorb/', include('Produkte.urls')),
    url(r'^veranstaltungen/', include(
        veranstaltungen_urls, 
        namespace='Veranstaltungen')),
    url(r'^salon/', include(
        salons_urls, 
        namespace='Veranstaltungen')),
    url(r'^seminare/', include(
        seminare_urls, 
        namespace='Veranstaltungen')),
    url(r'^bibliothek/', include('Bibliothek.urls')),
    url(r'^scholien/', include('Scholien.urls')),
    url(r'^spende/',
        ListeMitMenue.as_view(
            template_name='Produkte/spende.html',
            model=Spendenstufen,
            context_object_name = 'stufen'),
        name='gast_spende'),
    url(r'^geheim_db$',
        db_runterladen,
        name='bitte_bald_loeschen'),
    url(r'^', include('Grundgeruest.urls')),
]