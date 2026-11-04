from decimal import Decimal
from django.db import models, transaction
from django.core.exceptions import ValidationError

# Create your models here.
class CariHesap(models.Model):
    ad = models.CharField(max_length=100, verbose_name="Ad / Ünvan")
    soyad = models.CharField(max_length=100, blank=True, default="", verbose_name="Soyad / Yetkili")
    email = models.EmailField(blank=True, default="", verbose_name="E-posta")
    telefon = models.CharField(max_length=20, blank=True, default="", verbose_name="Telefon")
    adres = models.TextField(blank=True, default="", verbose_name="Adres")
    bakiye = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Bakiye (TL)")

    class Meta:
        verbose_name = "Cari Hesap"
        verbose_name_plural = "Cari Hesaplar"
        ordering = ['ad', 'soyad']

    @property
    def unvan(self):
        full = f"{self.ad} {self.soyad}".strip()
        return full if full else self.ad

    def __str__(self):
        return self.unvan


class Stok(models.Model):
    STOK_TIPLERI = [
        ('kilogram', 'kg (Kilogram)'),
        ('litre', 'lt (Litre)'),
        ('adet', 'Adet'),
        ('metre', 'Metre'),
        ('koli', 'Koli'),
    ]

    ad = models.CharField(max_length=100, verbose_name="Ürün Adı")
    aciklama = models.TextField(blank=True, default="", verbose_name="Açıklama")
    fiyat = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Birim Fiyat (TL)")
    stok_tipi = models.CharField(max_length=50, choices=STOK_TIPLERI, default='adet', verbose_name="Stok Tipi")
    stok_miktari = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Stok Miktarı")

    class Meta:
        verbose_name = "Stok / Ürün"
        verbose_name_plural = "Stoklar / Ürünler"
        ordering = ['ad']

    @property
    def miktar(self):
        return self.stok_miktari

    @property
    def birim(self):
        return self.get_stok_tipi_display()

    def __str__(self):
        return f"{self.ad} ({self.stok_miktari} {self.get_stok_tipi_display()})"


class Fatura(models.Model):
    cari_hesap = models.ForeignKey(CariHesap, on_delete=models.CASCADE, verbose_name="Cari Hesap")
    tarih = models.DateField(verbose_name="Fatura Tarihi")
    toplam_tutar = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Toplam Tutar")
    fatura_yonu = models.CharField(max_length=10, choices=[('alacak', 'Alacak'), ('borç', 'Borç')], verbose_name="Fatura Yönü")
    tahsilat_miktari = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Tahsilat Miktarı")
    tahsilat_durumu = models.BooleanField(default=False, verbose_name="Tahsilat Durumu")
    tahsilat_tarihi = models.DateField(null=True, blank=True, verbose_name="Tahsilat Tarihi")

    class Meta:
        verbose_name = "Fatura"
        verbose_name_plural = "Faturalar"
        ordering = ['-tarih', '-id']

    def save(self, *args, **kwargs):
        with transaction.atomic():
            kalan_tutar = self.toplam_tutar - self.tahsilat_miktari
            super().save(*args, **kwargs)
            if self.cari_hesap:
                if self.fatura_yonu == 'alacak':
                    self.cari_hesap.bakiye += kalan_tutar
                elif self.fatura_yonu == 'borç':
                    self.cari_hesap.bakiye -= kalan_tutar
                self.cari_hesap.save()

    def __str__(self):
        return f"Fatura #{self.id} - {self.cari_hesap.unvan}"


class FaturaKalem(models.Model):
    fatura = models.ForeignKey(Fatura, on_delete=models.CASCADE, related_name="kalemler")
    stok = models.ForeignKey(Stok, on_delete=models.CASCADE)
    miktar = models.DecimalField(max_digits=10, decimal_places=2)
    birim_fiyat = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.pk:
                if self.stok.stok_miktari >= self.miktar:
                    self.stok.stok_miktari -= self.miktar
                    self.stok.save()
                else:
                    raise ValueError("Yeterli stok yok.")
            super().save(*args, **kwargs)

    def toplam_tutar(self):
        return self.miktar * self.birim_fiyat

    def __str__(self):
        return f"{self.fatura} - {self.stok.ad} - {self.miktar}"


class Kasa(models.Model):
    ad = models.CharField(max_length=100, verbose_name="Kasa Adı")
    bakiye = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Bakiye")

    class Meta:
        verbose_name = "Kasa"
        verbose_name_plural = "Kasalar"

    def __str__(self):
        return f"{self.ad} ({self.bakiye} TL)"


class Islem(models.Model):
    ISLEM_TIPLERI = [
        ("alis", "Alış Faturası"),
        ("satis", "Satış Faturası")
    ]

    cari = models.ForeignKey(CariHesap, on_delete=models.CASCADE, verbose_name="Cari Hesap", related_name="islemler")
    stok = models.ForeignKey(Stok, on_delete=models.CASCADE, verbose_name="Ürün / Stok", related_name="islemler")
    islem_tipi = models.CharField(max_length=10, choices=ISLEM_TIPLERI, verbose_name="İşlem Tipi")
    miktar = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Miktar")
    birim_fiyat = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Birim Fiyat (TL)")
    tarih = models.DateTimeField(auto_now_add=True, verbose_name="İşlem Tarihi")
    notlar = models.TextField(blank=True, default="", verbose_name="Fatura Notu / Açıklama")

    class Meta:
        verbose_name = "İşlem / Fatura"
        verbose_name_plural = "İşlemler / Faturalar"
        ordering = ['-tarih']

    def toplam_tutar(self):
        if not self.miktar or not self.birim_fiyat:
            return Decimal('0.00')
        return (self.miktar * self.birim_fiyat).quantize(Decimal('0.01'))

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        with transaction.atomic():
            if is_new:
                # Alış: Stok artar, Carinin bakiyesi (borcumuz) azalır/değişir
                # Satış: Stok azalır, Carinin bakiyesi (alacağımız) artar
                tutar = self.miktar * self.birim_fiyat
                if self.islem_tipi == 'alis':
                    self.stok.stok_miktari += self.miktar
                    self.cari.bakiye -= tutar
                elif self.islem_tipi == 'satis':
                    self.stok.stok_miktari -= self.miktar
                    self.cari.bakiye += tutar
                self.stok.save()
                self.cari.save()
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            tutar = self.miktar * self.birim_fiyat
            if self.islem_tipi == 'alis':
                self.stok.stok_miktari -= self.miktar
                self.cari.bakiye += tutar
            elif self.islem_tipi == 'satis':
                self.stok.stok_miktari += self.miktar
                self.cari.bakiye -= tutar
            self.stok.save()
            self.cari.save()
            super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.get_islem_tipi_display()} - {self.cari.unvan} ({self.stok.ad})"