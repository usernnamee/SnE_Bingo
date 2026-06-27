import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_CENTER

input = "entries.txt"
output = "bingo_cards.pdf"

c_count = 500
size = 5

c_row = 2
c_col = 2
c_page = 3


def load_entries(file):
    with open(file, "r", encoding="utf-8") as f:
        pool = [line.strip() for line in f if line.strip()]
    return pool


def generate_card(pool):
    sample = random.sample(pool, 24)

    board = [["" for _ in range(size)] for _ in range(size)]

    k = 0
    for r in range(size):
        for c in range(size):
            if r == 2 and c == 2:
                board[r][c] = "FREE"
            else:
                board[r][c] = sample[k]
                k += 1

    return board


def draw_text(pdf, text, x, y, w, h, free=False):
    sheet = getSampleStyleSheet()
    form = sheet["Normal"]

    form.alignment = TA_CENTER
    form.fontName = "Helvetica-Bold" if free else "Helvetica"
    form.fontSize = 10 if free else 9
    form.leading = form.fontSize + 1

    box = Paragraph(text, form)

    txtW, txtH = box.wrap(w - 6, 1000)

    scale = min(
        (w - 6) / txtW if txtW else 1,
        (h - 6) / txtH if txtH else 1,
        1
    )

    pdf.saveState()
    pdf.translate(x + w / 2, y + h / 2)
    pdf.scale(scale, scale)
    box.drawOn(pdf, -txtW / 2, -txtH / 2)
    pdf.restoreState()


def draw_board(pdf, board, x0, y0, slotW, slotH):
    title_h = 0.30 * inch

    grid = min(
        slotW - 0.2 * inch,
        slotH - title_h - 0.2 * inch
    )

    cell = grid / size

    left = x0 + (slotW - grid) / 2
    top = y0 + slotH - title_h - cell

    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawCentredString(
        x0 + slotW / 2,
        y0 + slotH - 0.15 * inch,
        "S&E Project Presentations Bingo"
    )

    for r in range(size):
        for c in range(size):
            x = left + c * cell
            y = top - r * cell

            pdf.rect(x, y, cell, cell)

            text = board[r][c]
            draw_text(pdf, text, x, y, cell, cell, free=(text == "FREE"))


pool = load_entries(input)

if len(pool) < 24:
    raise ValueError("entries.txt must contain at least 24 entries.")

doc = canvas.Canvas(output, pagesize=letter)

page_w, page_h = letter

margin = 0.4 * inch
gap = 0.3 * inch

slotW = (page_w - 2 * margin - gap) / c_row
slotH = (page_h - 2 * margin - gap) / c_col

for i in range(c_count):
    page_pos = i % c_page

    row = page_pos // c_row
    col = page_pos % c_row

    x0 = margin + col * (slotW + gap)
    y0 = page_h - margin - (row + 1) * slotH - row * gap

    board = generate_card(pool)
    draw_board(doc, board, x0, y0, slotW, slotH)

    if page_pos == c_page - 1:
        doc.showPage()

if c_count % c_page != 0:
    doc.showPage()

doc.save()

print(f"Generated {c_count} bingo cards in '{output}'.")