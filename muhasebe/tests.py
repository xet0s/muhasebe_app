from decimal import Decimal
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import CariHesap, Islem, Stok


class MuhasebeSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.cari = CariHesap.objects.create(
            ad='Atlas Bilişim',
            soyad='Ltd. Şti.',
            email='info@atlasbilisim.com',
            telefon='05551234567',
            adres='Levent, İstanbul',
            bakiye=Decimal('1000.00')
        )
        self.stok = Stok.objects.create(
            ad='Ofis Koltuğu',
            aciklama='Ergonomik fileli çalışma koltuğu',
            fiyat=Decimal('2500.00'),
            stok_tipi='adet',
            stok_miktari=Decimal('20.00')
        )

    # 1. AUTHENTICATION TESTS
    def test_unauthenticated_access_redirects_to_login(self):
        urls = [
            reverse('dashboard'),
            reverse('cari-hesap-list'),
            reverse('stok-listesi'),
            reverse('islem-listesi'),
            reverse('cari-ekle'),
            reverse('stok-ekle'),
            reverse('islem-ekle'),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn('/login/', response.url)

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_failure(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Geçersiz kullanıcı adı veya şifre')

    def test_logout(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    # 2. CARI TESTS & SEARCH
    def test_cari_list_and_search(self):
        self.client.login(username='testuser', password='password123')
        # Create another cari
        CariHesap.objects.create(ad='Delta Kimya', soyad='A.Ş.', telefon='05321112233')

        # List all
        response = self.client.get(reverse('cari-hesap-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Atlas Bilişim')
        self.assertContains(response, 'Delta Kimya')

        # Search for Atlas
        response_search = self.client.get(reverse('cari-hesap-list') + '?q=Atlas')
        self.assertContains(response_search, 'Atlas Bilişim')
        self.assertNotContains(response_search, 'Delta Kimya')

    def test_cari_create(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('cari-ekle'), {
            'ad': 'Marmara Lojistik',
            'soyad': 'A.Ş.',
            'email': 'lojistik@marmara.com',
            'telefon': '02123334455',
            'adres': 'Tuzla, İstanbul',
            'bakiye': '500.00'
        })
        self.assertRedirects(response, reverse('cari-hesap-list'))
        self.assertTrue(CariHesap.objects.filter(ad='Marmara Lojistik').exists())

    def test_cari_update(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('cari_guncelle', args=[self.cari.id]), {
            'ad': 'Atlas Bilişim ve Yazılım',
            'soyad': 'Ltd. Şti.',
            'email': 'destek@atlas.com',
            'telefon': '05551234567',
            'adres': 'Maslak, İstanbul',
            'bakiye': '1200.00'
        })
        self.assertRedirects(response, reverse('cari-hesap-list'))
        self.cari.refresh_from_db()
        self.assertEqual(self.cari.ad, 'Atlas Bilişim ve Yazılım')

    def test_cari_delete(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('cari_sil', args=[self.cari.id]))
        self.assertRedirects(response, reverse('cari-hesap-list'))
        self.assertFalse(CariHesap.objects.filter(id=self.cari.id).exists())

    # 3. STOK TESTS & SEARCH/FILTER
    def test_stok_list_and_search_filter(self):
        self.client.login(username='testuser', password='password123')
        Stok.objects.create(ad='Motor Yağı', stok_tipi='litre', fiyat=Decimal('350.00'), stok_miktari=Decimal('50.00'))

        # List all
        response = self.client.get(reverse('stok-listesi'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ofis Koltuğu')
        self.assertContains(response, 'Motor Yağı')

        # Search
        response_search = self.client.get(reverse('stok-listesi') + '?q=Koltuğu')
        self.assertContains(response_search, 'Ofis Koltuğu')
        self.assertNotContains(response_search, 'Motor Yağı')

        # Filter by stock type
        response_filter = self.client.get(reverse('stok-listesi') + '?stok_tipi=litre')
        self.assertContains(response_filter, 'Motor Yağı')
        self.assertNotContains(response_filter, 'Ofis Koltuğu')

    def test_stok_create(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('stok-ekle'), {
            'ad': 'Yazıcı Kartuşu',
            'aciklama': 'Siyah toner',
            'fiyat': '450.00',
            'stok_tipi': 'adet',
            'stok_miktari': '15.00'
        })
        self.assertRedirects(response, reverse('stok-listesi'))
        self.assertTrue(Stok.objects.filter(ad='Yazıcı Kartuşu').exists())

    # 4. ISLEM / FATURA & STOCK/BALANCE UPDATE TESTS
    def test_satis_faturasi_creation_and_stock_balance_effects(self):
        self.client.login(username='testuser', password='password123')
        initial_stock = self.stok.stok_miktari  # 20
        initial_balance = self.cari.bakiye     # 1000

        # Satış: 2 adet x 2500 TL = 5000 TL
        response = self.client.post(reverse('islem-ekle'), {
            'cari': self.cari.id,
            'stok': self.stok.id,
            'islem_tipi': 'satis',
            'miktar': '2.00',
            'birim_fiyat': '2500.00',
            'notlar': 'Peşin satış'
        })
        self.assertRedirects(response, reverse('islem-listesi'))

        self.stok.refresh_from_db()
        self.cari.refresh_from_db()

        # Stock should decrease by 2 -> 18
        self.assertEqual(self.stok.stok_miktari, initial_stock - Decimal('2.00'))
        # Cari balance should increase by 5000 -> 6000
        self.assertEqual(self.cari.bakiye, initial_balance + Decimal('5000.00'))

    def test_alis_faturasi_creation_and_stock_balance_effects(self):
        self.client.login(username='testuser', password='password123')
        initial_stock = self.stok.stok_miktari  # 20
        initial_balance = self.cari.bakiye     # 1000

        # Alış: 5 adet x 2000 TL = 10000 TL
        response = self.client.post(reverse('islem-ekle'), {
            'cari': self.cari.id,
            'stok': self.stok.id,
            'islem_tipi': 'alis',
            'miktar': '5.00',
            'birim_fiyat': '2000.00',
            'notlar': 'Tedarik alımı'
        })
        self.assertRedirects(response, reverse('islem-listesi'))

        self.stok.refresh_from_db()
        self.cari.refresh_from_db()

        # Stock should increase by 5 -> 25
        self.assertEqual(self.stok.stok_miktari, initial_stock + Decimal('5.00'))
        # Cari balance should decrease by 10000 -> -9000
        self.assertEqual(self.cari.bakiye, initial_balance - Decimal('10000.00'))

    def test_insufficient_stock_prevents_sale(self):
        self.client.login(username='testuser', password='password123')
        # Attempt to sell 50 items when only 20 are in stock
        response = self.client.post(reverse('islem-ekle'), {
            'cari': self.cari.id,
            'stok': self.stok.id,
            'islem_tipi': 'satis',
            'miktar': '50.00',
            'birim_fiyat': '2500.00'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Yetersiz stok')
        self.assertEqual(Islem.objects.count(), 0)

    # 5. PDF INVOICE GENERATION TEST
    def test_invoice_pdf_generation(self):
        self.client.login(username='testuser', password='password123')
        islem = Islem.objects.create(
            cari=self.cari,
            stok=self.stok,
            islem_tipi='satis',
            miktar=Decimal('3.00'),
            birim_fiyat=Decimal('2500.00'),
            notlar='Türkçe karakter testi: ÇÖŞİĞÜ çşığöü'
        )

        response = self.client.get(reverse('islem_pdf', args=[islem.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(len(response.content) > 1000)
        self.assertTrue(response.content.startswith(b'%PDF-'))

        # Also test download parameter
        response_dl = self.client.get(reverse('islem_pdf', args=[islem.id]) + '?download=1')
        self.assertEqual(response_dl.status_code, 200)
        self.assertIn('attachment;', response_dl['Content-Disposition'])

    # 6. DELETE INVOICE ROLLBACK TEST
    def test_islem_delete_rolls_back_stock_and_balance(self):
        self.client.login(username='testuser', password='password123')
        initial_stock = self.stok.stok_miktari
        initial_balance = self.cari.bakiye

        islem = Islem.objects.create(
            cari=self.cari,
            stok=self.stok,
            islem_tipi='satis',
            miktar=Decimal('4.00'),
            birim_fiyat=Decimal('2500.00')
        )
        # Delete invoice
        response = self.client.post(reverse('islem_sil', args=[islem.id]))
        self.assertRedirects(response, reverse('islem-listesi'))

        self.stok.refresh_from_db()
        self.cari.refresh_from_db()
        self.assertEqual(self.stok.stok_miktari, initial_stock)
        self.assertEqual(self.cari.bakiye, initial_balance)

    # 7. ENHANCED FILTERS TEST
    def test_cari_balance_filters(self):
        self.client.login(username='testuser', password='password123')
        CariHesap.objects.create(ad='Borclu Cari', soyad='A.Ş.', bakiye=Decimal('-500.00'))

        # Filter alacak (>0)
        res_alacak = self.client.get(reverse('cari-hesap-list') + '?durum=alacak')
        self.assertContains(res_alacak, 'Atlas Bilişim')
        self.assertNotContains(res_alacak, 'Borclu Cari')

        # Filter borc (<0)
        res_borc = self.client.get(reverse('cari-hesap-list') + '?durum=borc')
        self.assertContains(res_borc, 'Borclu Cari')
        self.assertNotContains(res_borc, 'Atlas Bilişim')

    def test_stok_level_filters(self):
        self.client.login(username='testuser', password='password123')
        Stok.objects.create(ad='Tükenen Malzeme', stok_miktari=Decimal('0.00'), fiyat=Decimal('100.00'))

        res_tukenmis = self.client.get(reverse('stok-listesi') + '?durum=tukenmis')
        self.assertContains(res_tukenmis, 'Tükenen Malzeme')
        self.assertNotContains(res_tukenmis, 'Ofis Koltuğu')
