import json
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify

from .form import CariHesapForm, IslemForm, LoginForm, StokForm
from .models import CariHesap, Islem, Stok
from .pdf_service import generate_invoice_pdf


# -------------------------------------------------------------
# AUTHENTICATION VIEWS
# -------------------------------------------------------------

def login_view(request):
    """Kullanıcı giriş ekranı"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"Hoş geldiniz, {user.first_name or user.username}!")
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')
        else:
            messages.error(request, "Geçersiz kullanıcı adı veya şifre girdiniz.")
    else:
        form = LoginForm(request)

    return render(request, 'muhasebe/login.html', {'form': form})


def logout_view(request):
    """Kullanıcı çıkış işlemi"""
    auth_logout(request)
    messages.info(request, "Oturumunuz başarıyla sonlandırıldı.")
    return redirect('login')


# -------------------------------------------------------------
# DASHBOARD
# -------------------------------------------------------------

@login_required(login_url='login')
def dashboard(request):
    cari_sayisi = CariHesap.objects.count()
    stok_sayisi = Stok.objects.count()
    islem_sayisi = Islem.objects.count()

    # Finansal özet hesaplamaları
    islemler = Islem.objects.all()
    toplam_satis = sum(
        (i.miktar * i.birim_fiyat for i in islemler if i.islem_tipi == 'satis'),
        Decimal('0.00')
    )
    toplam_alis = sum(
        (i.miktar * i.birim_fiyat for i in islemler if i.islem_tipi == 'alis'),
        Decimal('0.00')
    )
    toplam_bakiye = sum(
        (c.bakiye for c in CariHesap.objects.all()),
        Decimal('0.00')
    )

    son_islemler = Islem.objects.select_related('cari', 'stok').order_by('-tarih')[:7]
    kritik_stoklar = Stok.objects.filter(stok_miktari__lte=5).order_by('stok_miktari')[:5]

    context = {
        'cari_sayisi': cari_sayisi,
        'stok_sayisi': stok_sayisi,
        'islem_sayisi': islem_sayisi,
        'toplam_satis': toplam_satis,
        'toplam_alis': toplam_alis,
        'toplam_bakiye': toplam_bakiye,
        'son_islemler': son_islemler,
        'kritik_stoklar': kritik_stoklar,
    }
    return render(request, 'muhasebe/dashboard.html', context)


# -------------------------------------------------------------
# CARİ HESAP İŞLEMLERİ
# -------------------------------------------------------------

@login_required(login_url='login')
def cari_hesap_list(request):
    q = request.GET.get('q', '').strip()
    durum = request.GET.get('durum', '').strip()
    cariler = CariHesap.objects.all()

    if q:
        cariler = cariler.filter(
            Q(ad__icontains=q) |
            Q(soyad__icontains=q) |
            Q(email__icontains=q) |
            Q(telefon__icontains=q) |
            Q(adres__icontains=q)
        )

    if durum == 'alacak':
        cariler = cariler.filter(bakiye__gt=0)
    elif durum == 'borc':
        cariler = cariler.filter(bakiye__lt=0)
    elif durum == 'sifir':
        cariler = cariler.filter(bakiye=0)

    # İstatistikler
    all_cariler = CariHesap.objects.all()
    toplam_alacak = sum((c.bakiye for c in all_cariler if c.bakiye > 0), Decimal('0.00'))
    toplam_borc = sum((abs(c.bakiye) for c in all_cariler if c.bakiye < 0), Decimal('0.00'))
    net_bakiye = toplam_alacak - toplam_borc

    context = {
        'cariler': cariler,
        'q': q,
        'durum': durum,
        'total_count': cariler.count(),
        'toplam_alacak': toplam_alacak,
        'toplam_borc': toplam_borc,
        'net_bakiye': net_bakiye,
    }
    return render(request, 'muhasebe/cari_hesap.html', context)


@login_required(login_url='login')
def cari_ekle(request):
    if request.method == 'POST':
        form = CariHesapForm(request.POST)
        if form.is_valid():
            cari = form.save()
            messages.success(request, f"'{cari.unvan}' başarıyla eklendi.")
            return redirect('cari-hesap-list')
    else:
        form = CariHesapForm()
    return render(request, 'muhasebe/cari_ekle.html', {'form': form})


@login_required(login_url='login')
def cari_guncelle(request, pk):
    cari = get_object_or_404(CariHesap, pk=pk)
    if request.method == 'POST':
        form = CariHesapForm(request.POST, instance=cari)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{cari.unvan}' bilgileri güncellendi.")
            return redirect('cari-hesap-list')
    else:
        form = CariHesapForm(instance=cari)
    return render(request, 'muhasebe/cari_guncelle.html', {'form': form, 'cari': cari})


@login_required(login_url='login')
def cari_sil(request, pk):
    cari = get_object_or_404(CariHesap, pk=pk)
    if request.method == 'POST':
        unvan = cari.unvan
        cari.delete()
        messages.warning(request, f"'{unvan}' cari hesabı silindi.")
        return redirect('cari-hesap-list')
    return render(request, 'muhasebe/cari_sil_onay.html', {'cari': cari})


# -------------------------------------------------------------
# STOK İŞLEMLERİ
# -------------------------------------------------------------

@login_required(login_url='login')
def stok_list(request):
    q = request.GET.get('q', '').strip()
    stok_tipi = request.GET.get('stok_tipi', '').strip()
    durum = request.GET.get('durum', '').strip()

    stoklar = Stok.objects.all()
    if q:
        stoklar = stoklar.filter(
            Q(ad__icontains=q) |
            Q(aciklama__icontains=q)
        )
    if stok_tipi:
        stoklar = stoklar.filter(stok_tipi=stok_tipi)

    if durum == 'kritik':
        stoklar = stoklar.filter(stok_miktari__lte=5, stok_miktari__gt=0)
    elif durum == 'tukenmis':
        stoklar = stoklar.filter(stok_miktari__lte=0)
    elif durum == 'normal':
        stoklar = stoklar.filter(stok_miktari__gt=5)

    all_stoklar = Stok.objects.all()
    toplam_envanter_degeri = sum((s.stok_miktari * s.fiyat for s in all_stoklar), Decimal('0.00'))
    kritik_stok_sayisi = all_stoklar.filter(stok_miktari__lte=5).count()

    context = {
        'stoklar': stoklar,
        'q': q,
        'stok_tipi': stok_tipi,
        'durum': durum,
        'stok_tipleri': Stok.STOK_TIPLERI,
        'total_count': stoklar.count(),
        'toplam_envanter_degeri': toplam_envanter_degeri,
        'kritik_stok_sayisi': kritik_stok_sayisi,
    }
    return render(request, 'muhasebe/stok_listesi.html', context)


@login_required(login_url='login')
def stok_ekle(request):
    if request.method == 'POST':
        form = StokForm(request.POST)
        if form.is_valid():
            stok = form.save()
            messages.success(request, f"'{stok.ad}' başarıyla stoğa eklendi.")
            return redirect('stok-listesi')
    else:
        form = StokForm()
    return render(request, 'muhasebe/stok_ekle.html', {'form': form})


@login_required(login_url='login')
def stok_guncelle(request, pk):
    stok = get_object_or_404(Stok, pk=pk)
    if request.method == 'POST':
        form = StokForm(request.POST, instance=stok)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{stok.ad}' stok bilgileri güncellendi.")
            return redirect('stok-listesi')
    else:
        form = StokForm(instance=stok)
    return render(request, 'muhasebe/stok_guncelle.html', {'form': form, 'stok': stok})


@login_required(login_url='login')
def stok_sil(request, pk):
    stok = get_object_or_404(Stok, pk=pk)
    if request.method == 'POST':
        ad = stok.ad
        stok.delete()
        messages.warning(request, f"'{ad}' ürünü stoktan silindi.")
        return redirect('stok-listesi')
    return render(request, 'muhasebe/stok_sil_onay.html', {'stok': stok})


# -------------------------------------------------------------
# İŞLEM / FATURA İŞLEMLERİ
# -------------------------------------------------------------

@login_required(login_url='login')
def islem_list(request):
    q = request.GET.get('q', '').strip()
    islem_tipi = request.GET.get('islem_tipi', '').strip()
    baslangic = request.GET.get('baslangic', '').strip()
    bitis = request.GET.get('bitis', '').strip()

    islemler = Islem.objects.select_related('cari', 'stok').all()
    if q:
        islemler = islemler.filter(
            Q(cari__ad__icontains=q) |
            Q(cari__soyad__icontains=q) |
            Q(stok__ad__icontains=q) |
            Q(notlar__icontains=q)
        )
    if islem_tipi:
        islemler = islemler.filter(islem_tipi=islem_tipi)
    if baslangic:
        islemler = islemler.filter(tarih__date__gte=baslangic)
    if bitis:
        islemler = islemler.filter(tarih__date__lte=bitis)

    # Filtrelenen listeye ait istatistikler
    filtre_satis = sum((i.miktar * i.birim_fiyat for i in islemler if i.islem_tipi == 'satis'), Decimal('0.00'))
    filtre_alis = sum((i.miktar * i.birim_fiyat for i in islemler if i.islem_tipi == 'alis'), Decimal('0.00'))

    context = {
        'islemler': islemler,
        'q': q,
        'islem_tipi': islem_tipi,
        'baslangic': baslangic,
        'bitis': bitis,
        'total_count': islemler.count(),
        'filtre_satis': filtre_satis,
        'filtre_alis': filtre_alis,
    }
    return render(request, 'muhasebe/islem_listesi.html', context)


@login_required(login_url='login')
def islem_ekle(request):
    tip = request.GET.get('tip', 'satis')
    initial_data = {}
    if tip in ['alis', 'satis']:
        initial_data['islem_tipi'] = tip

    stoklar = Stok.objects.all()
    stok_map = {
        str(s.id): {
            'id': s.id,
            'ad': s.ad,
            'fiyat': float(s.fiyat),
            'stok_miktari': float(s.stok_miktari),
            'birim': s.get_stok_tipi_display(),
        }
        for s in stoklar
    }
    stok_map_json = json.dumps(stok_map)

    if request.method == 'POST':
        form = IslemForm(request.POST)
        if form.is_valid():
            islem = form.save(commit=False)
            # Satış faturası ise stok kontrolü
            if islem.islem_tipi == 'satis' and islem.stok.stok_miktari < islem.miktar:
                messages.error(
                    request,
                    f"Yetersiz stok! '{islem.stok.ad}' için mevcut stok: {islem.stok.stok_miktari} {islem.stok.birim}, talep edilen miktar: {islem.miktar}"
                )
                return render(request, 'muhasebe/islem_ekle.html', {
                    'form': form,
                    'stok_map_json': stok_map_json,
                    'tip': islem.islem_tipi,
                })

            islem.save()
            messages.success(request, f"#{islem.id} numaralı {islem.get_islem_tipi_display()} başarıyla kaydedildi.")
            return redirect('islem-listesi')
    else:
        form = IslemForm(initial=initial_data)

    return render(request, 'muhasebe/islem_ekle.html', {
        'form': form,
        'stok_map_json': stok_map_json,
        'tip': initial_data.get('islem_tipi', 'satis'),
    })


@login_required(login_url='login')
def islem_sil(request, pk):
    islem = get_object_or_404(Islem, pk=pk)
    if request.method == 'POST':
        islem_id = islem.id
        islem.delete()
        messages.warning(request, f"#{islem_id} numaralı fatura / işlem silindi ve stok/bakiye güncellendi.")
        return redirect('islem-listesi')
    return render(request, 'muhasebe/islem_sil_onay.html', {'islem': islem})


# -------------------------------------------------------------
# PDF FATURA ÇIKTISI
# -------------------------------------------------------------

@login_required(login_url='login')
def islem_pdf(request, pk):
    """Seçilen faturanın PDF çıktısını üretir"""
    islem = get_object_or_404(Islem.objects.select_related('cari', 'stok'), pk=pk)
    pdf_bytes = generate_invoice_pdf(islem)

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    download = request.GET.get('download') == '1'
    disposition = 'attachment' if download else 'inline'
    clean_name = slugify(islem.cari.ad) or f"cari_{islem.cari.id}"
    filename = f"fatura_{islem.id:05d}_{clean_name}.pdf"
    response['Content-Disposition'] = f'{disposition}; filename="{filename}"'
    return response
