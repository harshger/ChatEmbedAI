from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from datetime import datetime, timezone
import io
import logging

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from database import db
from auth_utils import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["invoices"])

COMPANY_INFO = {
    'name': 'ChatEmbed AI GmbH',
    'street': 'Musterstraße 42',
    'city': '10115 Berlin',
    'country': 'Deutschland',
    'vat_id': 'DE123456789',
    'tax_number': '27/123/45678',
    'email': 'billing@chatembed.ai',
    'bank': 'Deutsche Bank AG',
    'iban': 'DE89 3704 0044 0532 0130 00',
    'bic': 'COBADEFFXXX',
}

PLAN_NAMES_DE = {
    'starter': 'Starter Plan',
    'pro': 'Pro Plan',
    'agency': 'Agentur Plan',
    'free': 'Free Plan',
}

VAT_RATE = 0.19


def draw_invoice_pdf(buf, transaction, user):
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    klein_blue = HexColor('#002FA7')
    black = HexColor('#0A0A0A')
    gray = HexColor('#4B5563')
    light_gray = HexColor('#E5E7EB')

    # Header bar
    c.setFillColor(klein_blue)
    c.rect(0, h - 28 * mm, w, 28 * mm, fill=1, stroke=0)

    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont('Helvetica-Bold', 18)
    c.drawString(20 * mm, h - 18 * mm, 'RECHNUNG')
    c.setFont('Helvetica', 9)
    c.drawRightString(w - 20 * mm, h - 13 * mm, COMPANY_INFO['name'])
    c.drawRightString(w - 20 * mm, h - 17 * mm, f"{COMPANY_INFO['street']}, {COMPANY_INFO['city']}")
    c.drawRightString(w - 20 * mm, h - 21 * mm, f"USt-IdNr.: {COMPANY_INFO['vat_id']}")

    y = h - 45 * mm

    # Invoice metadata
    tx_id = transaction.get('transaction_id', '')
    invoice_number = f"CE-{tx_id[:8].upper()}"
    created = transaction.get('created_at', '')
    invoice_date = created[:10] if created else datetime.now(timezone.utc).strftime('%Y-%m-%d')

    c.setFillColor(black)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(20 * mm, y, 'Rechnungsnummer:')
    c.setFont('Helvetica', 10)
    c.drawString(70 * mm, y, invoice_number)

    y -= 6 * mm
    c.setFont('Helvetica-Bold', 10)
    c.drawString(20 * mm, y, 'Rechnungsdatum:')
    c.setFont('Helvetica', 10)
    c.drawString(70 * mm, y, invoice_date)

    y -= 6 * mm
    c.setFont('Helvetica-Bold', 10)
    c.drawString(20 * mm, y, 'Zahlungsstatus:')
    c.setFont('Helvetica', 10)
    status = transaction.get('payment_status', 'unknown')
    status_text = 'Bezahlt' if status == 'paid' else status.capitalize()
    c.drawString(70 * mm, y, status_text)

    y -= 14 * mm

    # Customer info
    c.setFont('Helvetica-Bold', 10)
    c.drawString(20 * mm, y, 'Rechnungsempfänger:')
    y -= 6 * mm
    c.setFont('Helvetica', 10)
    c.drawString(20 * mm, y, user.get('full_name', user.get('email', '')))
    y -= 5 * mm
    if user.get('company_name'):
        c.drawString(20 * mm, y, user['company_name'])
        y -= 5 * mm
    c.drawString(20 * mm, y, user.get('email', ''))
    y -= 5 * mm
    if user.get('website_url'):
        c.setFillColor(gray)
        c.drawString(20 * mm, y, user['website_url'])
        c.setFillColor(black)

    y -= 14 * mm

    # Table header
    c.setFillColor(klein_blue)
    c.rect(20 * mm, y - 1 * mm, w - 40 * mm, 8 * mm, fill=1, stroke=0)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont('Helvetica-Bold', 9)
    c.drawString(22 * mm, y + 1 * mm, 'Beschreibung')
    c.drawRightString(w - 80 * mm, y + 1 * mm, 'Menge')
    c.drawRightString(w - 50 * mm, y + 1 * mm, 'Netto')
    c.drawRightString(w - 22 * mm, y + 1 * mm, 'Gesamt')

    y -= 10 * mm

    # Line item
    amount = transaction.get('amount', 0)
    net_amount = round(amount / (1 + VAT_RATE), 2)
    vat_amount = round(amount - net_amount, 2)
    plan = transaction.get('plan', 'starter')
    plan_name = PLAN_NAMES_DE.get(plan, plan.capitalize() + ' Plan')

    c.setFillColor(black)
    c.setFont('Helvetica', 9)
    c.drawString(22 * mm, y + 1 * mm, f"{plan_name} — Monatliches Abonnement")
    c.drawRightString(w - 80 * mm, y + 1 * mm, '1')
    c.drawRightString(w - 50 * mm, y + 1 * mm, f"{net_amount:.2f} EUR")
    c.drawRightString(w - 22 * mm, y + 1 * mm, f"{net_amount:.2f} EUR")

    y -= 8 * mm
    c.setStrokeColor(light_gray)
    c.line(20 * mm, y, w - 20 * mm, y)

    y -= 10 * mm

    # Subtotals
    c.setFont('Helvetica', 9)
    c.setFillColor(gray)
    c.drawRightString(w - 50 * mm, y, 'Zwischensumme (netto):')
    c.setFillColor(black)
    c.drawRightString(w - 22 * mm, y, f"{net_amount:.2f} EUR")

    y -= 6 * mm
    c.setFillColor(gray)
    c.drawRightString(w - 50 * mm, y, f"Umsatzsteuer ({int(VAT_RATE * 100)}%):")
    c.setFillColor(black)
    c.drawRightString(w - 22 * mm, y, f"{vat_amount:.2f} EUR")

    y -= 2 * mm
    c.setStrokeColor(klein_blue)
    c.setLineWidth(1.5)
    c.line(w - 80 * mm, y, w - 20 * mm, y)

    y -= 8 * mm
    c.setFont('Helvetica-Bold', 11)
    c.setFillColor(klein_blue)
    c.drawRightString(w - 50 * mm, y, 'Gesamtbetrag (brutto):')
    c.drawRightString(w - 22 * mm, y, f"{amount:.2f} EUR")

    # Footer with bank info
    y -= 30 * mm
    c.setStrokeColor(light_gray)
    c.setLineWidth(0.5)
    c.line(20 * mm, y, w - 20 * mm, y)

    y -= 8 * mm
    c.setFillColor(gray)
    c.setFont('Helvetica', 8)
    c.drawString(20 * mm, y, f"Bankverbindung: {COMPANY_INFO['bank']} | IBAN: {COMPANY_INFO['iban']} | BIC: {COMPANY_INFO['bic']}")
    y -= 5 * mm
    c.drawString(20 * mm, y, f"Steuernummer: {COMPANY_INFO['tax_number']} | USt-IdNr.: {COMPANY_INFO['vat_id']}")
    y -= 5 * mm
    c.drawString(20 * mm, y, f"{COMPANY_INFO['name']} | {COMPANY_INFO['street']} | {COMPANY_INFO['city']} | {COMPANY_INFO['email']}")
    y -= 8 * mm
    c.setFont('Helvetica', 7)
    c.drawString(20 * mm, y, 'Hinweis: Diese Rechnung wurde maschinell erstellt und ist ohne Unterschrift gültig (§ 14 UStG).')
    y -= 5 * mm
    c.drawString(20 * mm, y, 'Aufbewahrungspflicht gemäß § 257 HGB: 10 Jahre.')

    c.save()


@router.get("/billing/invoice/{transaction_id}/pdf")
async def download_invoice_pdf(transaction_id: str, user=Depends(get_current_user)):
    tx = await db.payment_transactions.find_one(
        {'transaction_id': transaction_id, 'user_id': user['user_id']},
        {'_id': 0}
    )
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if tx.get('payment_status') != 'paid':
        raise HTTPException(status_code=400, detail="Invoice only available for paid transactions")

    buf = io.BytesIO()
    draw_invoice_pdf(buf, tx, user)
    pdf_bytes = buf.getvalue()

    invoice_number = f"CE-{transaction_id[:8].upper()}"
    created = tx.get('created_at', '')
    date_str = created[:10] if created else datetime.now(timezone.utc).strftime('%Y-%m-%d')
    filename = f"Rechnung-{invoice_number}-{date_str}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
