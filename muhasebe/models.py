from django.db import models

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
    stok_miktari = models.IntegerField()
    def __str__(self):
        return self.ad

