from django.contrib import admin
from .models import CariHesap, Stok, Fatura, FaturaKalem, Kasa
# Register your models here.

admin.site.register(CariHesap)
admin.site.register(Stok)
admin.site.register(Fatura)
admin.site.register(FaturaKalem)
admin.site.register(Kasa)