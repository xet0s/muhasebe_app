from django.db import models
from django.db import transaction
from decimal import Decimal

# Create your models here.
class CariHesap(models.Model):
    ad = models.CharField(max_length=100)
    soyad = models.CharField(max_length=100)
    email = models.EmailField()
    telefon = models.CharField(max_length=20)
    adres = models.TextField()
    bakiye = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"{self.ad} {self.soyad}"

class Stok(models.Model):
    ad = models.CharField(max_length=100)
    aciklama = models.TextField()
    fiyat = models.DecimalField(max_digits=10, decimal_places=2)
    stok_tipi = models.CharField(max_length=50, choices=[('kilogram', 'kg'), ('litre', 'lt'), ('adet', 'adet')])
    stok_miktari = models.IntegerField()
    def __str__(self):
        return self.ad

class Fatura(models.Model):
    cari_hesap = models.ForeignKey(CariHesap, on_delete=models.CASCADE)
    tarih = models.DateField()
    toplam_tutar = models.DecimalField(max_digits=10, decimal_places=2)
    fatura_yonu = models.CharField(max_length=10, choices=[('alacak', 'Alacak'), ('borç', 'Borç')])
    tahsilat_miktari = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tahsilat_durumu = models.BooleanField(default=False)
    tahsilat_tarihi = models.DateField(null=True, blank=True)
    def save(self, *args, **kwargs):
        with transaction.atomic():
            kalan_tutar = self.toplam_tutar - self.tahsilat_miktari
            super().save(*args, **kwargs)
            if self.cari_hesap:
                self.cari_hesap.bakiye += kalan_tutar
                self.cari_hesap.save()

            if self.tahsilat_miktari and self.tahsilat_miktari > 0:
                if self.fatura_yonu == 'alacak':
                    self.cari_hesap.bakiye -= self.tahsilat_miktari
                elif self.fatura_yonu == 'borç':
                    self.cari_hesap.bakiye += self.tahsilat_miktari
                self.cari_hesap.save()
            
    
    
    
    def __str__(self):
        return f"Fatura {self.id} - {self.cari_hesap.ad} {self.cari_hesap.soyad}"

class FaturaKalem(models.Model):
    fatura = models.ForeignKey(Fatura, on_delete=models.CASCADE)
    stok = models.ForeignKey(Stok, on_delete=models.CASCADE)
    miktar = models.IntegerField()
    birim_fiyat = models.DecimalField(max_digits=10, decimal_places=2)
    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.pk:
                if self.stok.stok_miktari < self.miktar:
                    self.stok.stok_miktari-= self.miktar
                    self.stok.save()
                else:
                    raise ValueError("Yeterli stok yok.")
            super().save(*args, **kwargs)
    
    
    def __str__(self):
        return f"{self.fatura} - {self.stok.ad} - {self.miktar} adet"

class Kasa(models.Model):
    ad = models.CharField(max_length=100)
    bakiye = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.ad