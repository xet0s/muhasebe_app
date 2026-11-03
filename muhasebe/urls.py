from django.urls import path
from .views import dashboard
from .views import cari_hesap_list

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('cari-hesaplar/', cari_hesap_list, name='cari-hesap-list'),
]