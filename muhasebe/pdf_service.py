import io
import os
from decimal import Decimal
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Font configuration for Turkish character support
FONT_NAME = 'Helvetica'
FONT_NAME_BOLD = 'Helvetica-Bold'

CANDIDATE_FONTS = [
    ('/usr/share/fonts/TTF/DejaVuSans.ttf', '/usr/share/fonts/TTF/DejaVuSans-Bold.ttf'),
    ('/usr/share/fonts/dejavu/DejaVuSans.ttf', '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf'),
    ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
    ('/usr/share/fonts/liberation/LiberationSans-Regular.ttf', '/usr/share/fonts/liberation/LiberationSans-Bold.ttf'),
]

for regular_path, bold_path in CANDIDATE_FONTS:
    if os.path.exists(regular_path) and os.path.exists(bold_path):
        try:
            pdfmetrics.registerFont(TTFont('MuhasebeFont', regular_path))
            pdfmetrics.registerFont(TTFont('MuhasebeFont-Bold', bold_path))
            FONT_NAME = 'MuhasebeFont'
            FONT_NAME_BOLD = 'MuhasebeFont-Bold'
            break
        except Exception:
            pass


def generate_invoice_pdf(islem):
    """
    Generates a professional PDF invoice for the given Islem object.
    Returns bytes of the PDF.
    """
    buffer = io.BytesIO()

    # Document setup with A4 margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor('#1e3a8a')  # Dark blue
    success_color = colors.HexColor('#047857')  # Emerald
    warning_color = colors.HexColor('#b45309')  # Amber
    dark_gray = colors.HexColor('#1f2937')
    light_gray = colors.HexColor('#6b7280')
    border_color = colors.HexColor('#e5e7eb')

    is_satis = (islem.islem_tipi == 'satis')
    type_color = success_color if is_satis else primary_color

    style_company = ParagraphStyle(
        'Company',
        fontName=FONT_NAME_BOLD,
        fontSize=16,
        leading=20,
        textColor=primary_color
    )
    style_subtitle = ParagraphStyle(
        'CompanySub',
        fontName=FONT_NAME,
        fontSize=8,
        leading=11,
        textColor=light_gray
    )
    style_inv_title = ParagraphStyle(
        'InvTitle',
        fontName=FONT_NAME_BOLD,
        fontSize=15,
        leading=18,
        alignment=2,  # Right aligned
        textColor=type_color
    )
    style_inv_meta = ParagraphStyle(
        'InvMeta',
        fontName=FONT_NAME,
        fontSize=8.5,
        leading=12,
        alignment=2,
        textColor=dark_gray
    )
    style_section_title = ParagraphStyle(
        'SecTitle',
        fontName=FONT_NAME_BOLD,
        fontSize=10,
        leading=13,
        textColor=primary_color
    )
    style_label = ParagraphStyle(
        'Label',
        fontName=FONT_NAME_BOLD,
        fontSize=8.5,
        leading=12,
        textColor=light_gray
    )
    style_val = ParagraphStyle(
        'Value',
        fontName=FONT_NAME,
        fontSize=8.5,
        leading=12,
        textColor=dark_gray
    )
    style_val_bold = ParagraphStyle(
        'ValueBold',
        fontName=FONT_NAME_BOLD,
        fontSize=8.5,
        leading=12,
        textColor=dark_gray
    )
    style_tbl_head = ParagraphStyle(
        'TblHead',
        fontName=FONT_NAME_BOLD,
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )
    style_tbl_cell = ParagraphStyle(
        'TblCell',
        fontName=FONT_NAME,
        fontSize=8.5,
        leading=11,
        textColor=dark_gray
    )
    style_tbl_cell_r = ParagraphStyle(
        'TblCellR',
        fontName=FONT_NAME,
        fontSize=8.5,
        leading=11,
        alignment=2,
        textColor=dark_gray
    )
    style_tbl_cell_bold_r = ParagraphStyle(
        'TblCellBoldR',
        fontName=FONT_NAME_BOLD,
        fontSize=9,
        leading=12,
        alignment=2,
        textColor=dark_gray
    )
    style_footer = ParagraphStyle(
        'Footer',
        fontName=FONT_NAME,
        fontSize=7.5,
        leading=10,
        alignment=1,
        textColor=light_gray
    )

    story = []

    # 1. HEADER SECTION
    invoice_title_text = "SATIŞ FATURASI" if is_satis else "ALIŞ FATURASI"
    fatura_no = f"FTR-{islem.tarih.year if islem.tarih else 2026}-{islem.id:06d}"
    tarih_str = islem.tarih.strftime("%d.%m.%Y %H:%M") if islem.tarih else "-"

    left_header = [
        Paragraph("ÖN MUHASEBE YÖNETİM SİSTEMİ", style_company),
        Spacer(1, 2),
        Paragraph("Ticari Faaliyetler ve Cari Hesap Yönetimi", style_subtitle),
        Paragraph("Vergi Kimlik / Şirket Bilgilendirme Belgesi", style_subtitle),
    ]

    right_header = [
        Paragraph(invoice_title_text, style_inv_title),
        Spacer(1, 4),
        Paragraph(f"<b>Fatura No:</b> {fatura_no}", style_inv_meta),
        Paragraph(f"<b>Tarih:</b> {tarih_str}", style_inv_meta),
        Paragraph(f"<b>Durum:</b> Onaylandı / Kaydedildi", style_inv_meta),
    ]

    header_table = Table(
        [[left_header, right_header]],
        colWidths=[105 * mm, 75 * mm]
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    # Divider Line
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=4, spaceAfter=12))

    # 2. CARI INFORMATION & BILLING DETAILS BOX
    cari = islem.cari
    cari_unvan = cari.unvan if cari else "Belirtilmemiş Cari"
    cari_telefon = cari.telefon if (cari and cari.telefon) else "Belirtilmemiş"
    cari_email = cari.email if (cari and cari.email) else "Belirtilmemiş"
    cari_adres = cari.adres if (cari and cari.adres) else "Belirtilmemiş"
    cari_bakiye = f"{cari.bakiye:,.2f} TL" if cari else "0.00 TL"

    cari_box_data = [
        [
            Paragraph("<b>MÜŞTERİ / CARİ BİLGİLERİ</b>", style_section_title),
            Paragraph("<b>İŞLEM VE HESAP DETAYI</b>", style_section_title),
        ],
        [
            Paragraph(f"<b>Cari Adı / Ünvan:</b> {cari_unvan}", style_val_bold),
            Paragraph(f"<b>Cari Kodu:</b> CARI-{cari.id:05d}" if cari else "-", style_val),
        ],
        [
            Paragraph(f"<b>Telefon:</b> {cari_telefon}", style_val),
            Paragraph(f"<b>Cari Güncel Bakiye:</b> {cari_bakiye}", style_val_bold),
        ],
        [
            Paragraph(f"<b>E-posta:</b> {cari_email}", style_val),
            Paragraph(f"<b>İşlem Türü:</b> {islem.get_islem_tipi_display()}", style_val),
        ],
        [
            Paragraph(f"<b>Adres:</b> {cari_adres}", style_val),
            Paragraph(f"<b>Ödeme Türü:</b> Cari Hesaba Mahsuben", style_val),
        ],
    ]

    cari_table = Table(cari_box_data, colWidths=[100 * mm, 80 * mm])
    cari_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.8, border_color),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8fafc')),
        ('LINEBELOW', (0, 0), (-1, 0), 0.8, border_color),
        ('LINEBEFORE', (1, 0), (1, -1), 0.8, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(cari_table)
    story.append(Spacer(1, 14))

    # 3. ITEMS TABLE
    story.append(Paragraph("<b>FATURA KALEMLERİ</b>", style_section_title))
    story.append(Spacer(1, 4))

    toplam_tutar = islem.toplam_tutar() if callable(getattr(islem, 'toplam_tutar', None)) else islem.toplam_tutar
    if toplam_tutar is None:
        toplam_tutar = Decimal('0.00')

    # Calculate subtotal and VAT (%20 included)
    kdv_orani = Decimal('0.20')
    ara_toplam = (toplam_tutar / (Decimal('1') + kdv_orani)).quantize(Decimal('0.01'))
    kdv_tutari = (toplam_tutar - ara_toplam).quantize(Decimal('0.01'))

    stok = islem.stok
    stok_ad = stok.ad if stok else "Belirtilmemiş Ürün"
    stok_birim = stok.get_stok_tipi_display() if stok else "Adet"

    items_data = [
        [
            Paragraph("Sıra", style_tbl_head),
            Paragraph("Ürün / Hizmet Açıklaması", style_tbl_head),
            Paragraph("Birim", style_tbl_head),
            Paragraph("Miktar", style_tbl_head),
            Paragraph("Birim Fiyat", style_tbl_head),
            Paragraph("KDV", style_tbl_head),
            Paragraph("Toplam", style_tbl_head),
        ],
        [
            Paragraph("1", style_tbl_cell),
            Paragraph(f"<b>{stok_ad}</b>", style_tbl_cell),
            Paragraph(stok_birim, style_tbl_cell),
            Paragraph(f"{islem.miktar}", style_tbl_cell_r),
            Paragraph(f"{islem.birim_fiyat:,.2f} TL", style_tbl_cell_r),
            Paragraph("%20", style_tbl_cell_r),
            Paragraph(f"<b>{toplam_tutar:,.2f} TL</b>", style_tbl_cell_r),
        ]
    ]

    items_table = Table(
        items_data,
        colWidths=[12 * mm, 62 * mm, 22 * mm, 18 * mm, 22 * mm, 16 * mm, 28 * mm]
    )
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 10))

    # 4. TOTALS SUMMARY & NOTES
    notlar_text = islem.notlar if getattr(islem, 'notlar', None) else "Bu işlem sistem muhasebe kayıtlarına doğrudan yansıtılmıştır."

    notes_box = [
        Paragraph("<b>Açıklama / Fatura Notu:</b>", style_label),
        Spacer(1, 2),
        Paragraph(notlar_text, style_val),
    ]

    totals_data = [
        [Paragraph("Ara Toplam (KDV Hariç):", style_val), Paragraph(f"{ara_toplam:,.2f} TL", style_val_bold)],
        [Paragraph("Hesaplanan KDV (%20):", style_val), Paragraph(f"{kdv_tutari:,.2f} TL", style_val_bold)],
        [Paragraph("<b>GENEL TOPLAM:</b>", style_section_title), Paragraph(f"<b>{toplam_tutar:,.2f} TL</b>", style_tbl_cell_bold_r)],
    ]

    totals_table = Table(totals_data, colWidths=[45 * mm, 35 * mm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#f1f5f9')),
        ('BOX', (0, 0), (-1, -1), 0.8, border_color),
        ('LINEBELOW', (0, 0), (-1, 1), 0.5, border_color),
    ]))

    summary_table = Table(
        [[notes_box, totals_table]],
        colWidths=[100 * mm, 80 * mm]
    )
    summary_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 25))

    # 5. SIGNATURE & STAMP AREA
    sign_data = [
        [
            Paragraph("<b>DÜZENLEYEN / TESLİM EDEN</b>", style_section_title),
            Paragraph("<b>TESLİM ALAN (CARİ / MÜŞTERİ)</b>", style_section_title),
        ],
        [
            Paragraph("İsim / İmza / Kaşe:<br/><br/><br/>________________________________", style_val),
            Paragraph("İsim / İmza / Kaşe:<br/><br/><br/>________________________________", style_val),
        ]
    ]
    sign_table = Table(sign_data, colWidths=[90 * mm, 90 * mm])
    sign_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(KeepTogether(sign_table))
    story.append(Spacer(1, 20))

    # 6. FOOTER
    story.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceBefore=4, spaceAfter=6))
    story.append(Paragraph(
        "Bu fatura ve işlem makbuzu Ön Muhasebe Sistemi tarafından elektronik olarak oluşturulmuştur. &bull; Sayfa 1/1",
        style_footer
    ))

    # Build document
    doc.build(story)
    return buffer.getvalue()

