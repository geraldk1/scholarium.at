from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse

# Create your views here.

from easycart import BaseCart, BaseItem
from Grundgeruest.views import erstelle_liste_menue
from .models import Kauf, Produkt

"""
Integration des Pakets easycart - keine Modelle, über session Variablen

Idee der built-in-Implementation:
 - warenkorb wird in der session als JSON-string gespeichert
 - für Bearbeitung wird der Konstruktor von BaseCart aufgerufen und bekommt
   den request, und damit die session, übergeben
 - zum Speichern wird cart.encode() ausgeführt um das rückwärts auszuführen
 - im kodierten Zustand haben wir im Wesentlichen ein dict (pk -> quantity)
 - pk bezieht sich auf ein Modell, also alle Produkte in einer DB-Tabelle
 - im geladenen Zustand eine Instanz von Cart, cart.items ist ein dict von
   Items, die wiederum haben item.obj (Instanz vom Produkt-Modell) und 
   item.quantity
 - Preis wird aus einem Attribut der obj-Instanz ausgelesen, mit Methoden 
   von Item und Cart validiert und von Cart aus aufgerufen
 - beim Laden wird eine Cart instanziiert aus request; cart.create_items()
   instantiiert die items, wobei cart.get_queryset(pks) aufgerufen wird und
   den DB-lookup ausführt um die item.obj zu befüllen.
 - auch bei add/change_quantity wird get_queryset() aufgerufen
 - konkret aufgerufen werden die Methoden, indem die url an den view weiter
   leitet, der mit den POST-Parameter die Fkt der Cart-Instanz aufruft.
 - offene Frage: wann wird Cart instantiiert, bei Severstart, oder...?
   
   
Änderungen:
 - nur ein pk ist unbefriedigend, wir haben ein Tupel von drei:
   art (Veranstaltung/Buch/etc) + id + typ (Teilnahme/Livestream) 
 - es muss offensichtlich get_queryset() und encode() geändert werden, da 
   item.obj jetzt aus zwei Werten (Tabelle und Zeile) gelesen wird. Eine
   Menge anderes gibt dann auch probleme; elegante Lösung s. unten...
 - zur Philosophie: ist ein "tradeoff" ... ist nicht schön, dass die Klasse
   Veranstaltung Daten enthält, die nix mit der Veranstaltung zu tun haben, 
   wie Preis oder besetzte Plätze; aber alternativ muss man zu jedem Objekt
   ein extra Produkt erstellen, welches (zumeist leere) Verknüpfungen zu 
   den verschiedenen produktfähigen Klassen hat...
 - Konkret die Umsetzung, um möglichst wenig zu ändern. Achtung, jetzt 
   wird's kompliziert:
   - die urls werden an andere views geleitet; als POST-Parameter erwarte 
     ich immer noch nur pk (String mit drei Werten) und optional quantity.
   - der CartView, von dem die konkreten views erben, zerteilt die pk und 
     gibt redundant sowohl den ganzen pk (die braucht die Cart-Instanz um 
     die als keys der items-dict zu nehmen) als auch die art (die wird als
     optionaler kwarg interpretiert und automatisch an den Item-Konstruktor
     weitergeleitet). So muss ich nur get_queryset und encode ändern, und 
     den Konstruktor und __repr__ vom Item. 
     - z.B. Cart.add bekommt die Parameter pk, quantity, art, holt sich obj
     über die pk, und fügt Item(...) zum items-dict unter dem key pk hinzu.
"""

class Ware(BaseItem):
    def __init__(self, obj, quantity=1, **kwargs):
        if not 'art' in kwargs:
            kwargs.update([('art', 1)])
        self._quantity = self.clean_quantity(quantity)
        #pdb.set_trace()
        self.price = obj.preis_ausgeben(kwargs['art'])
        self.obj = obj
        for key, value in kwargs.items():
            setattr(self, key, value)
        self._kwargs = kwargs

    def __repr__(self):
        main_args = 'obj={}, art={}, quantity={}'.format(
            self.obj, 
            self._kwargs['art'], 
            self.quantity)
        extra_args = ['{}={}'.format(k, getattr(self, k)) for k in self._kwargs]
        args_repr = ', '.join([main_args] + extra_args)
        return  '<Ware: ' + args_repr + '>'


class Warenkorb(BaseCart):
    item_class = Ware
    
    @staticmethod
    def tupel_aus_pk(pk):
        model_name, obj_pk, art = str(pk).split('; ')
        return model_name, obj_pk, art

    @staticmethod
    def tupel_zu_pk(tupel_pk):
        model_name, obj_pk, art = [str(x) for x in tupel_pk]
        return '; '.join([model_name, obj_pk, art])    
    
    def get_queryset(self, pks):
        """ Liest Objekte aus den übergebenen pks aus 
        jeder pk wird in drei Teile zerlegt und die ersten beiden verwendet
        um die Tabelle an der richtigen Zeile auszulesen """
        objekte = []
        for pk in pks:
            model_name, obj_pk, art = self.tupel_aus_pk(pk)
            model = ContentType.objects.get(model=model_name)
            objekte.append(model.get_object_for_this_type(pk=obj_pk))
        return objekte

    def encode(self, formatter=None):
        """ fast übernommen aus der Ursprungsimplementierung
        Nur Konstruktion von pk (als key für items verwendet) erweitert


        Return a representation of the cart as a JSON-response.

        Parameters
        ----------
        formatter : func, optional
            A function that accepts the cart representation and returns
            its formatted version.

        Returns
        -------
        django.http.JsonResponse

        Examples
        --------
        Assume that items with primary keys "1" and "4" are already in
        the cart.

        >>> cart = Cart(request)
        >>> def format_total_price(cart_repr):
        ...     return intcomma(cart_repr['totalPrice'])
        ...
        >>> json_response = cart.encode(format_total_price)
        >>> json_response.content
        b'{
            "items": {
                '1': {"price": 100, "quantity": 10, "total": 1000},
                '4': {"price": 50, "quantity": 20, "total": 1000},
            },
            "itemCount": 2,
            "totalPrice": "2,000",
        }'

        """
        items = {}
        # The prices are converted to strings, because they may have a
        # type that can't be serialized to JSON (e.g. Decimal).
        for item in self.items.values():
            model_name = item.obj.__class__.__name__.lower()
            obj_pk = item.obj.pk
            art = item._kwargs['art']
            pk = self.tupel_zu_pk((model_name, obj_pk, art))
            items[pk] = {
                'price': str(item.price),
                'quantity': item.quantity,
                'total': item.total,
            }
        cart_repr = {
            'items': items,
            'itemCount': self.item_count,
            'totalPrice': str(self.total_price),
        }
        if formatter:
            cart_repr = formatter(cart_repr)
        return JsonResponse(cart_repr)

    def create_items(self, session_items):
        """fast übernommen aus der Ursprungsimplementierung
        Nur verhindert, dass pk (als key für items verwendet) mit obj.pk
        überschrieben wird; vorher war die Funktion dafür nicht darauf 
        angewiesen, dass get_queryset die obj zu den pks in der passenden
        Reihenfolge zurückgibt; das tut's aber jetzt (war ursprünglich 
        queryset, bei mit Liste), insofern ist das okay.
        
        Instantiate cart items from session data.

        The value returned by this method is used to populate the
        cart's `items` attribute.

        Parameters
        ----------
        session_items : dict
            A dictionary of pk-quantity mappings (each pk is a string).
            For example: ``{'1': 5, '3': 2}``.

        Returns
        -------
        dict
            A map between the `session_items` keys and instances of
            :attr:`item_class`. For example::

                {'1': <CartItem: obj=foo, quantity=5>,
                 '3': <CartItem: obj=bar, quantity=2>}

        """
        pks = list(session_items.keys())
        items = {}
        item_class = self.item_class
        process_object = self.process_object
        # die eine Zeile geändert:
        for pk, obj in zip(pks, self.get_queryset(pks)):
            obj = process_object(obj)
            items[pk] = item_class(obj, **session_items[pk])
        if len(items) < len(session_items):
            self._stale_pks = set(session_items).difference(items)
        return items


@login_required
def bestellungen(request):
    nutzer = request.user.my_profile
    liste_menue = erstelle_liste_menue(request.user)
    kaeufe = Kauf.objects.filter(nutzer=nutzer)
    medien = [kauf for kauf in kaeufe if kauf.produkt.zu_medium]
    veranstaltungen = [kauf for kauf in kaeufe if kauf.produkt.zu_veranstaltung]
    return render(request, 
        'Produkte/bestellungen.html', 
        {'medien': medien, 
            'veranstaltungen': veranstaltungen, 
            'liste_menue': liste_menue,
        })

def kaufen(request):
    warenkorb = Warenkorb(request)
    nutzer = request.user.my_profile
    if nutzer.guthaben < warenkorb.count_total_price():
        return HttpResponse('Guthaben reicht nicht aus!') # das schöner machen!
    
    waren = warenkorb.list_items()
    for ware in waren:
        guthaben = nutzer.guthaben
        kauf = Kauf.objects.create(
            nutzer=nutzer,
            produkt_id=ware.obj.pk,
            menge=ware.quantity,
            guthaben_davor=guthaben)
        nutzer.guthaben = guthaben - ware.total
        nutzer.save()
        warenkorb.remove(ware.obj.pk)
        
    return HttpResponseRedirect(reverse('Produkte:warenkorb'))
    
