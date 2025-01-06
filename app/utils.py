from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generate_ticket_pdf(data: dict) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, f"Seat: {data["seat"]}")
    c.drawString(100, 725, f"Price: {data["price"]}")
    c.drawString(100, 700, f"Town from: {data["town_from"]}")
    c.drawString(100, 675, f"Town to: {data["town_to"]}")
    c.drawString(100, 650, f"Time out: {data["time_out"]:%m/%d/%Y %H:%M}")
    c.drawString(100, 625, f"Time in: {data["time_in"]:%m/%d/%Y %H:%M}")
    c.drawString(100, 600, f"Airport: {data["airport"]}")
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
