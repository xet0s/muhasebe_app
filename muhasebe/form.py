from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CariHesap, Islem, Stok


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Kullanıcı Adı",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Kullanıcı adınızı girin',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label="Şifre",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Şifrenizi girin'
        })
    )


class CariHesapForm(forms.ModelForm):
    class Meta:
        model = CariHesap
        fields = ["ad", "soyad", "email", "telefon", "adres", "bakiye"]
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Şirket Adı veya Ad'}),
            'soyad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Yetkili veya Soyad'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'iletisim@firma.com'}),
            'telefon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '05xx xxx xx xx'}),
            'adres': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Açık adres bilgisi'}),
            'bakiye': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        help_texts = {
            'bakiye': 'Müşterinin/tedarikçinin mevcut bakiyesi (TL). Satışlar bakiyeyi artırır, alışlar azaltır.'
        }


class StokForm(forms.ModelForm):
    class Meta:
        model = Stok
        fields = ['ad', 'aciklama', 'fiyat', 'stok_tipi', 'stok_miktari']
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Örn: A4 Fotokopi Kağıdı'}),
            'aciklama': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ürün detayları, marka, model vb.'}),
            'fiyat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'stok_tipi': forms.Select(attrs={'class': 'form-select'}),
            'stok_miktari': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
        }


class IslemForm(forms.ModelForm):
    class Meta:
        model = Islem
        fields = ['cari', 'stok', 'islem_tipi', 'miktar', 'birim_fiyat', 'notlar']
        widgets = {
            'cari': forms.Select(attrs={'class': 'form-select'}),
            'stok': forms.Select(attrs={'class': 'form-select'}),
            'islem_tipi': forms.Select(attrs={'class': 'form-select'}),
            'miktar': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'placeholder': '1.00'}),
            'birim_fiyat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.00', 'placeholder': '0.00'}),
            'notlar': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'İsteğe bağlı fatura / işlem notu'}),
        }
