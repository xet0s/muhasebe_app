from django.urls import path
from .views import (
    dashboard,
    login_view,
    logout_view,
    cari_hesap_list,
    cari_ekle,
    cari_guncelle,
    cari_sil,
    stok_list,
    stok_ekle,
    stok_guncelle,
    stok_sil,
    islem_list,
    islem_ekle,
    islem_sil,
    islem_pdf,
)

urlpatterns = [
    # Dashboard & Auth
    path('', dashboard, name='dashboard'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Cari Hesaplar
    path('cari-hesaplar/', cari_hesap_list, name='cari-hesap-list'),
    path('cari-hesap-list/', cari_hesap_list, name='cari_hesap_list'),
    path('cari-ekle/', cari_ekle, name='cari-ekle'),
    path('cari_ekle/', cari_ekle, name='cari_ekle'),
    path('cari-guncelle/<int:pk>/', cari_guncelle, name='cari_guncelle'),
    path('cari_guncelle/<int:pk>/', cari_guncelle, name='cari-guncelle'),
    path('cari-sil/<int:pk>/', cari_sil, name='cari_sil'),
    path('cari_sil/<int:pk>/', cari_sil, name='cari-sil'),

    # Stoklar
    path('stoklar/', stok_list, name='stok-listesi'),
    path('stok-listesi/', stok_list, name='stok_listesi'),
    path('stok-ekle/', stok_ekle, name='stok-ekle'),
    path('stok_ekle/', stok_ekle, name='stok_ekle'),
    path('stok-guncelle/<int:pk>/', stok_guncelle, name='stok_guncelle'),
    path('stok_guncelle/<int:pk>/', stok_guncelle, name='stok-guncelle'),
    path('stok-sil/<int:pk>/', stok_sil, name='stok_sil'),
    path('stok_sil/<int:pk>/', stok_sil, name='stok-sil'),

    # İşlemler / Faturalar
    path('islem-listesi/', islem_list, name='islem-listesi'),
    path('islemler/', islem_list, name='islem_listesi'),
    path('islem-ekle/', islem_ekle, name='islem-ekle'),
    path('islem_ekle/', islem_ekle, name='islem_ekle'),
    path('islem-sil/<int:pk>/', islem_sil, name='islem_sil'),
    path('islem_sil/<int:pk>/', islem_sil, name='islem-sil'),
    path('islem/<int:pk>/pdf/', islem_pdf, name='islem_pdf'),
    path('islem-pdf/<int:pk>/', islem_pdf, name='islem-pdf'),
]
