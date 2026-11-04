from django.contrib import admin
from .models import CariHesap, Stok, Fatura, FaturaKalem, Kasa, Islem


@admin.register(CariHesap)
class CariHesapAdmin(admin.ModelAdmin):
    list_display = ('unvan', 'telefon', 'email', 'bakiye')
    search_fields = ('ad', 'soyad', 'telefon', 'email', 'adres')
    list_filter = ('bakiye',)


@admin.register(Stok)
class StokAdmin(admin.ModelAdmin):
    list_display = ('ad', 'fiyat', 'stok_miktari', 'stok_tipi')
    search_fields = ('ad', 'aciklama')
    list_filter = ('stok_tipi',)


@admin.register(Islem)
class IslemAdmin(admin.ModelAdmin):
    list_display = ('id', 'tarih', 'cari', 'stok', 'islem_tipi', 'miktar', 'birim_fiyat', 'toplam_tutar')
    list_filter = ('islem_tipi', 'tarih')
    search_fields = ('cari__ad', 'cari__soyad', 'stok__ad', 'notlar')
    date_hierarchy = 'tarih'


admin.site.register(Fatura)
admin.site.register(FaturaKalem)
admin.site.register(Kasa)
