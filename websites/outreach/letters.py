#!/usr/bin/env python3
"""
Generate print-ready postal outreach letters, one page per business, as a
single US Letter PDF.

Run with the project venv:
    .venv/bin/python3 letters.py

Requires: segno (QR codes), reportlab (PDF layout). Both are pure-Python /
pip-installable without sudo; see websites/outreach/.venv.

Data sources per business:
  - Letter body content adapted from the matching .md draft in this folder.
  - Business name + street address read from
    websites/sites/<slug>/FACTS.json (claims.address.value).
  - Preview URL read directly out of the .md draft (the link James already
    sent would-be recipients by email; unchanged here).
"""

import json
import os
import re
import textwrap

import segno
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

BASE = os.path.dirname(os.path.abspath(__file__))
SITES_DIR = os.path.normpath(os.path.join(BASE, "..", "sites"))
OUT_PDF = os.path.join(BASE, "letters_2026-09-16.pdf")
QR_TMP_DIR = os.path.join(BASE, ".qr_tmp")

SENDER_NAME = "James"
SENDER_COMPANY = "Cascade Web Design"
SENDER_ADDRESS_LINE1 = "7146 NE 154th Ave"
SENDER_ADDRESS_LINE2 = "Vancouver, WA 98682"
LETTER_DATE = "September 16, 2026"

FOOTER_TEXT = (
    "You are receiving this because your business is publicly listed. "
    "Write STOP on this letter and mail it back, or call, and you will "
    "not hear from me again."
)

# slug -> (preview URL, feature line used in the body, city used in the body)
BUSINESSES = [
    {
        "slug": "daves-auto-care",
        "name": "Dave's Auto Care",
        "url": "https://daves-auto-care.vercel.app",
        "city": "Portland",
        "feature": "It is built to get your phone ringing, not just to look nice.",
    },
    {
        "slug": "harveys-auto-service",
        "name": "Harvey's Auto Service",
        "url": "https://harveys-auto-service.vercel.app",
        "city": "Seattle",
        "feature": "It is built to get your phone ringing, not just to look nice.",
    },
    {
        "slug": "andys-auto-repair",
        "name": "Andy's Auto Repair",
        "url": "https://andys-auto-repair-psi.vercel.app",
        "city": "Seattle",
        "feature": (
            "It has your hours, your specialties, and a big call button, "
            "built for someone searching auto repair Seattle on their "
            "phone to call you instead of the next shop on the list."
        ),
    },
    {
        "slug": "master-mechanics",
        "name": "Master Mechanics",
        "url": "https://master-mechanics-three.vercel.app",
        "city": "Portland",
        "feature": (
            "It has your hours, your services, and a big call button, "
            "built for someone searching auto repair Portland on their "
            "phone to call you instead of the next shop on the list."
        ),
    },
    {
        "slug": "pipes-are-us",
        "name": "Pipes Are Us",
        "url": "https://pipes-are-us.vercel.app",
        "city": "Fresno",
        "feature": (
            "It has your hours and your services, with a big call "
            "button built to get people on the phone with you instead "
            "of the next plumber on Google."
        ),
    },
]


def load_address(slug):
    """Read the street address for a business out of its FACTS.json."""
    facts_path = os.path.join(SITES_DIR, slug, "FACTS.json")
    with open(facts_path) as f:
        facts = json.load(f)
    address = facts["claims"]["address"]["value"]
    # Address strings are "Street, City, ST ZIP" -- split into a street
    # line and a city/state/zip line for the letter's recipient block.
    parts = [p.strip() for p in address.split(",")]
    if len(parts) >= 3:
        street = parts[0]
        city_state_zip = ", ".join(parts[1:])
    else:
        # Fallback: shouldn't happen given the known data, but don't crash.
        street = address
        city_state_zip = ""
    return street, city_state_zip, address


def make_body(biz):
    return (
        "Hi,\n\n"
        f"I build websites for local {biz['city']} shops that do not have "
        f"one yet, and I noticed {biz['name']} does not have a site. So I "
        "built you one already, no charge, to look at first. You can see "
        "it below.\n\n"
        f"{biz['feature']}\n\n"
        "If you want it live on your own domain, it is $499 one time to "
        "set up, plus $39 a month for hosting and any edits. Call me and "
        "I will have it live within a day.\n\n"
        "No obligation either way. The preview is yours to look at "
        "regardless of what you decide.\n\n"
        "James"
    )


def word_count(text):
    return len(text.split())


def wrap_paragraph(text, font_name, font_size, max_width):
    """Word-wrap a single paragraph (no embedded newlines) to max_width."""
    words = text.split(" ")
    lines = []
    current = ""
    for w in words:
        candidate = (current + " " + w).strip()
        if stringWidth(candidate, font_name, font_size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def draw_wrapped(c, text, x, y, font_name, font_size, leading, max_width):
    """Draw a multi-paragraph block (paragraphs separated by blank lines),
    wrapping each paragraph to max_width. Returns the y position after the
    last line drawn."""
    c.setFont(font_name, font_size)
    paragraphs = text.split("\n\n")
    for i, para in enumerate(paragraphs):
        lines = wrap_paragraph(para, font_name, font_size, max_width)
        for line in lines:
            c.drawString(x, y, line)
            y -= leading
        if i != len(paragraphs) - 1:
            y -= leading * 0.4  # paragraph gap
    return y


def build_qr_png(url, slug):
    os.makedirs(QR_TMP_DIR, exist_ok=True)
    path = os.path.join(QR_TMP_DIR, f"{slug}.png")
    qr = segno.make(url, error="m")
    qr.save(path, scale=12, border=4, dark="black", light="white")
    return path


def draw_letter(c, biz):
    width, height = LETTER
    left = 1 * inch
    right = width - 1 * inch
    content_width = right - left
    top = height - 1 * inch

    y = top

    # --- Sender block, top-left ---
    c.setFont("Helvetica-Bold", 11)
    c.drawString(left, y, SENDER_NAME)
    y -= 14
    c.setFont("Helvetica", 11)
    c.drawString(left, y, SENDER_COMPANY)
    y -= 14
    c.drawString(left, y, SENDER_ADDRESS_LINE1)
    y -= 14
    c.drawString(left, y, SENDER_ADDRESS_LINE2)
    y -= 28

    # --- Date ---
    c.setFont("Helvetica", 11)
    c.drawString(left, y, LETTER_DATE)
    y -= 26

    # --- Recipient block: business name + street address ---
    street, city_state_zip, _full = load_address(biz["slug"])
    c.setFont("Helvetica-Bold", 11)
    c.drawString(left, y, biz["name"])
    y -= 14
    c.setFont("Helvetica", 11)
    c.drawString(left, y, street)
    y -= 14
    c.drawString(left, y, city_state_zip)
    y -= 30

    # --- Letter body ---
    body = make_body(biz)
    y = draw_wrapped(c, body, left, y, "Helvetica", 11, 15, content_width)
    y -= 20

    # --- Preview URL, large type ---
    c.setFont("Helvetica-Bold", 18)
    url_width = stringWidth(biz["url"], "Helvetica-Bold", 18)
    c.drawString(left + (content_width - url_width) / 2, y, biz["url"])
    y -= 34

    # --- QR code (>= 1.4in, using 1.6in) + caption ---
    qr_size = 1.6 * inch
    qr_path = build_qr_png(biz["url"], biz["slug"])
    qr_x = left + (content_width - qr_size) / 2
    qr_y = y - qr_size
    c.drawImage(
        qr_path, qr_x, qr_y, width=qr_size, height=qr_size,
        preserveAspectRatio=True, mask="auto",
    )
    caption_y = qr_y - 16
    c.setFont("Helvetica-Oblique", 10)
    caption = "Scan to see your site"
    caption_width = stringWidth(caption, "Helvetica-Oblique", 10)
    c.drawString(left + (content_width - caption_width) / 2, caption_y, caption)

    # --- Footer, fixed near the bottom margin ---
    footer_font = "Helvetica-Oblique"
    footer_size = 9
    footer_leading = 12
    footer_lines = wrap_paragraph(FOOTER_TEXT, footer_font, footer_size, content_width)
    footer_y = 0.65 * inch + footer_leading * (len(footer_lines) - 1)
    c.setFont(footer_font, footer_size)
    for line in footer_lines:
        line_width = stringWidth(line, footer_font, footer_size)
        c.drawString(left + (content_width - line_width) / 2, footer_y, line)
        footer_y -= footer_leading


def main():
    # Sanity-check body word counts before rendering anything.
    for biz in BUSINESSES:
        body = make_body(biz)
        wc = word_count(body)
        print(f"{biz['slug']}: body word count = {wc}")
        assert wc < 160, f"{biz['slug']} body is {wc} words, must be under 160"

    c = canvas.Canvas(OUT_PDF, pagesize=LETTER)
    c.setTitle("Outreach letters - 2026-09-16")
    for biz in BUSINESSES:
        draw_letter(c, biz)
        c.showPage()
    c.save()
    print(f"Wrote {OUT_PDF}")


if __name__ == "__main__":
    main()
