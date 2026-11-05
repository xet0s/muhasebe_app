# 💼 Ön Muhasebe ve Cari/Stok Yönetim Sistemi

[![Django](https://img.shields.io/badge/Django-6.1-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![ReportLab](https://img.shields.io/badge/PDF_Engine-ReportLab-DA291C?style=for-the-badge)](https://www.reportlab.com/)
[![Database](https://img.shields.io/badge/Database-SQLite%20%7C%20PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

KOBİ'ler, serbest çalışanlar ve işletmeler için geliştirilmiş; cari hesap, stok takibi, fatura kesimi, otomatik fiyatlandırma ve profesyonel PDF çıktı özelliklerine sahip modern bir web tabanlı **Ön Muhasebe Yönetim Sistemi**.

---

## ✨ Temel Özellikler

### 1. 📊 Gösterge Paneli (Dashboard)
- **Finansal KPI Kartları:** Toplam cari sayısı, stok çeşidi, kesilen fatura adedi ve toplam satış hacmi (ciro).
- **Finansal Özet:** Toplam satış tutarı, toplam alış tutarı ve cari hesapların genel alacak/borç dengesi.
- **Hızlı İşlemler:** Tek tıkla Satış Faturası, Alış Faturası, Yeni Cari veya Stok Kartı ekleme kısayolları.
- **Kritik Stok Takibi:** Depo mevcudu kritik seviyede (&le; 5) olan ürünlerin anlık uyarı paneli.
- **Son İşlemler:** Kesilen son faturaların dökümü ve tek tıkla PDF çıktı butonları.

### 2. 👥 Cari Hesap Yönetimi
- Müşteri ve tedarikçi bilgilerinin (Ünvan, Yetkili, Telefon, E-posta, Adres) detaylı takibi.
- **Dinamik Bakiye Sistemi:** Yapılan satışlar alacak bakiyesini (+), alışlar borç bakiyesini (-) anlık günceller.
- **Gelişmiş Arama:** Cari adı, yetkili, telefon, e-posta veya adrese göre anında filtreleme.
- **Bakiye Durumu Filtreleri:** Alacaklı olduklarımız (+), borçlu olduklarımız (-) ve sıfır bakiyeliler.
- **Cari Hareketleri Kısayolu:** Her carinin satırından o cariye ait tüm geçmiş fatura dökümüne doğrudan geçiş.

### 3. 📦 Stok ve Depo Yönetimi
- Ürün kartı tanımlama, açıklama, birim satış fiyatı ve birim tipi (Adet, kg, litre, metre, koli).
- **Toplam Envanter Değeri:** Depodaki tüm ürünlerin güncel finansal varlık değerinin otomatik hesaplanması.
- **Stok Durum Filtresi:** Kritik stoklar (&le; 5), tükenmiş ürünler (0) veya yeterli stoklar.
- **Stok Hareket Geçmişi:** İlgili ürünün hangi faturada kaç adet alınıp satıldığını listeleme kısayolu.

### 4. 🧾 Fatura ve Mali İşlemler
- **Alış ve Satış Faturaları:** Her fatura kesildiğinde stok miktarı ve cari bakiye otomatik senkronize olur. Fatura silindiğinde stok ve bakiye otomatik geri alınır (rollback).
- **Otomatik Birim Fiyat Seçimi:** Satış faturası düzenlerken ürün seçildiği anda tanımlı liste satış fiyatı (`stok.fiyat`) birim fiyat alanına otomatik yüklenir. İstenirse manuel indirim uygulanabilir veya tek tıkla liste fiyatına dönülebilir.
- **Canlı Stok Uyarısı:** Satış esnasında talep edilen miktar depodaki mevcuttan fazla ise ekranda anlık kırmızı uyarı verilir ve işlem kilitlenir.
- **Canlı Toplam Hesaplayıcı:** Miktar ve birim fiyat girildiği anda JavaScript ile anlık toplam tutar hesaplaması.
- **Filtreleme & Arama:** Metin araması, işlem türü (Alış/Satış) ve iki tarih arası (Başlangıç/Bitiş) filtreleme.

### 5. 📄 Profesyonel PDF Fatura Çıktısı
- **ReportLab** motoruyla Türkçe karakter desteği (DejaVuSans font entegrasyonu).
- Kurumsal antet, seri/sıra numarası (`#FTR-YYYY-XXXXX`), cari ve vergi bilgileri, ürün kalem tablosu, KDV hesaplamaları, fatura notu ve teslim eden/alan kaşe-imza bölümleri.
- Tarayıcıda doğrudan açma (Önizleme/Yazdır) ve PDF dosyası olarak cihaza indirme desteği.

### 6. 🔐 Kullanıcı Girişi ve Güvenlik (Authentication)
- Oturum açma (Login) ve oturumu sonlandırma (Logout) mekanizması.
- Tüm muhasebe sayfalarında `@login_required` güvenliği (giriş yapmayan kullanıcılar login sayfasına yönlendirilir).
- CSRF koruması ve güvenli form doğrulama.

---

## 🏗️ Mimari ve Teknolojiler

```
muhasebe_app/
├── config/                  # Django proje ayarları
│   ├── settings.py          # Otomatik DB fallback (Postgres/SQLite), Auth & Locale
│   ├── urls.py              # Kök URL yönlendiricisi
│   └── wsgi.py
├── muhasebe/                # Muhasebe çekirdek uygulaması
│   ├── models.py            # CariHesap, Stok, Islem, Fatura, Kasa
│   ├── views.py             # Dashboard, CRUD, arama/filtreleme ve PDF görünümleri
│   ├── urls.py              # Uygulama içi URL eşlemeleri (alias destekli)
│   ├── form.py              # Bootstrap stilli ModelForm'lar ve LoginForm
│   ├── pdf_service.py       # ReportLab A4 fatura üretim servisi
│   ├── admin.py             # Gelişmiş Django Admin yapılandırması
│   ├── tests.py             # 17 adet uçtan uca otomatik test
│   └── templates/muhasebe/  # Bootstrap 5 responsive şablonlar
│       ├── base.html        # Ortak layout, responsive navbar, flash mesajlar
│       ├── login.html       # Giriş ekranı
│       ├── dashboard.html   # Yönetim paneli ve KPI özetleri
│       ├── cari_*.html      # Cari listesi, ekleme, güncelleme, silme
│       ├── stok_*.html      # Stok listesi, ekleme, güncelleme, silme
│       └── islem_*.html     # Fatura listesi, ekleme, silme
├── requirements.txt         # Python bağımlılık listesi
└── manage.py
```

### Akıllı Veritabanı Desteği (Database Fallback)
Proje, `settings.py` üzerinde otomatik bağlantı denetimine sahiptir:
- Eğer yerel veya uzak makinede **PostgreSQL** çalışıyorsa otomatik olarak PostgreSQL'e bağlanır.
- PostgreSQL çalışmıyorsa veya yerel geliştirmede bulunuluyorsa uygulama çökmez; sorunsuz bir şekilde **SQLite** veritabanına geçer.

---

## 🚀 Kurulum ve Çalıştırma

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/kullanici-adiniz/muhasebe_app.git
cd muhasebe_app
```

### 2. Sanal Ortamı Oluşturun ve Aktifleştirin

**Bash / Zsh için:**
```bash
python -m venv .venv
source .venv/bin/activate
```

**Fish Shell için:**
```fish
python -m venv .venv
source .venv/bin/activate.fish
```

### 3. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 4. Veritabanı Migrasyonlarını Uygulayın
```bash
python manage.py migrate
```

### 5. Geliştirme Sunucusunu Başlatın
```bash
python manage.py runserver
```
*(Alternatif olarak `.venv` içerisindeki Python ile doğrudan çalıştırmak için: `.venv/bin/python manage.py runserver`)*

Tarayıcınızdan **`http://127.0.0.1:8000/`** adresini açın.

---

## 🔑 Varsayılan Yönetici Bilgileri

Sisteme ilk girişte kullanabileceğiniz ön tanımlı hesap:
- **Kullanıcı Adı:** `admin`
- **Şifre:** `admin123`

*(Yeni bir yönetici hesabı oluşturmak isterseniz: `python manage.py createsuperuser`)*

---

## 🧪 Testlerin Çalıştırılması

Tüm iş mantığını, stok düşüş/artış kontrollerini, yetki denetimlerini ve PDF üretimini test etmek için:

```bash
python manage.py test muhasebe
```

Çıktı örneği:
```text
Found 17 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.................
----------------------------------------------------------------------
Ran 17 tests in 8.567s

OK
Destroying test database for alias 'default'...
```

---

## 💡 İpuçları ve Port Sorunları

Eğer sunucuyu başlatırken `Error: That port is already in use` hatası alırsanız:
1. Başka bir terminalde çalışan `runserver` oturumunu `Ctrl + C` ile kapatın veya portu boşaltın:
   ```bash
   fuser -k 8000/tcp
   ```
2. Ya da sunucuyu boş olan başka bir portta başlatın:
   ```bash
   python manage.py runserver 8001
   ```

---

## 📄 Lisans
Bu proje [MIT Lisansı](LICENSE) kapsamında açık kaynak olarak sunulmaktadır.

