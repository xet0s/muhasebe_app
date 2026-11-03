from django.shortcuts import render
from .models import CariHesap, Stok, Fatura, FaturaKalem, Kasa
# Create your views here.

def dashboard(request):
    toplam_kasa = sum(kasa.bakiye for kasa in Kasa.objects.all())

    toplam_cari_hesap = CariHesap.objects.count()
    toplam_stok = Stok.objects.count()

    son_faturalar = Fatura.objects.order_by('-tarih')[:5]

    context = {
        'toplam_kasa': toplam_kasa,
        'toplam_cari_hesap': toplam_cari_hesap,
        'toplam_stok': toplam_stok,
        'son_faturalar': son_faturalar,
    }
    return render(request, 'muhasebe/dashboard.html')

def cari_hesap_list(request):
    cariler = CariHesap.objects.all()
    context = {
        'cariler': cariler
    }
    return render(request, 'muhasebe/cari_hesap.html', context)
