from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from guardian.admin import GuardedModelAdmin
from userena.models import UserenaSignup
from .forms import ZahlungFormular

from .models import Hauptpunkt, Unterpunkt, ScholariumProfile, Mitwirkende, Unterstuetzung


class StufenPlusUnterstuetzerListFilter(admin.SimpleListFilter):  # Nicht in Benutzung, Unterstützung.stufe ist nicht mehr möglich.
    """
    This filter extends the common list_filter = ('stufe') by the option
    "Unterstützer (alle)", i.e. stufe > 0.
    """
    title = 'Stufe'
    parameter_name = 'stufe'

    extended_stufe_choices = ScholariumProfile.stufe_choices.copy()
    extended_stufe_choices.insert(1, ('unterstuetzer', 'Unterstützer (alle)'))

    def lookups(self, request, model_admin):
        return self.extended_stufe_choices

    def queryset(self, request, queryset):
        if self.value() == 'unterstuetzer':
            return queryset.filter(stufe__gte=1)
        else:
            for stufe_nr, stufe_name in self.extended_stufe_choices:
                if self.value() == str(stufe_nr):
                    return queryset.filter(stufe__exact=stufe_nr)


class UnterstuetzungInline(admin.TabularInline):
    model = Unterstuetzung
    ordering = ['-datum']
    readonly_fields = ['ablauf', 'methode']
    extra = 0

    def ablauf(self, obj):
        return obj.get_ablauf()

    def methode(self, obj):
        return dict(ZahlungFormular.payment_choices).get(obj.zahlungsmethode) or obj.zahlungsmethode


class ProfileAdmin(admin.ModelAdmin):
    list_filter = ['land']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    list_display = ['anrede', 'user', 'guthaben', 'get_Status', 'get_aktiv', 'get_ablauf']
    inlines = [UnterstuetzungInline]


admin.site.register(ScholariumProfile, ProfileAdmin)


class UnterpunktInline(admin.TabularInline):
    model = Unterpunkt
    fields = ('bezeichnung', 'slug')
    extra = 1


class HauptpunktAdmin(admin.ModelAdmin):
    inlines = [UnterpunktInline]


class UnterstuetzungAdmin(admin.ModelAdmin):
    model = Unterstuetzung
    search_fields = ['profil__user__email',
                     'profil__user__first_name',
                     'profil__user__last_name']
    list_display = ('stufe', 'profil', 'datum', 'zahlungsmethode')
    list_filter = ['datum', 'stufe']


admin.site.register(Hauptpunkt, HauptpunktAdmin)
admin.site.register(Unterpunkt)
admin.site.register(Mitwirkende)
admin.site.register(Unterstuetzung, UnterstuetzungAdmin)


# von userena.admin kopiert und angepasst

class UserenaSignupInline(admin.StackedInline):
    model = UserenaSignup
    max_num = 1


class ProfileInline(admin.StackedInline):
    model = ScholariumProfile
    max_num = 1


class UserenaAdmin(UserAdmin, GuardedModelAdmin):
    inlines = [UserenaSignupInline, ProfileInline]
    list_display = ('email', 'first_name', 'last_name',
                    'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')


admin.site.register(get_user_model(), UserenaAdmin)

'''
geht nicht:

class KaufInline(admin.TabularInline):
    model = Kauf
    fields = ('datum', 'produkt_pk')
    extra = 1
'''
