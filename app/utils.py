from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .models import Payment


def generate_ticket_pdf(data: dict) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, f"Seat: {data["seat"]}")
    c.drawString(100, 725, f"Price: {data["price"]}")
    c.drawString(100, 700, f"Town from: {data["town_from"]}")
    c.drawString(100, 675, f"Airport: {data["airport_from"]}")
    c.drawString(100, 650, f"Town to: {data["town_to"]}")
    c.drawString(100, 625, f"Airport: {data["airport_to"]}")
    c.drawString(100, 600, f"Time out: {data["time_out"]:%m/%d/%Y %H:%M}")
    c.drawString(100, 575, f"Time in: {data["time_in"]:%m/%d/%Y %H:%M}")
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

def generate_seats_map(seats: list) ->dict:
    seat_map = {'business': {}, 'economy': {}} 
    for seat in seats: 
        row_number = int(seat.number[:-1])
        if seat.seat_class == 'business': 
            if row_number not in seat_map['business']: 
                seat_map['business'][row_number] = [] 
            seat_map['business'][row_number].append(seat) 
        else: 
            if row_number not in seat_map['economy']: 
                seat_map['economy'][row_number] = [] 
            seat_map['economy'][row_number].append(seat)
    
    return seat_map

def generate_items_for_payment(stripe, payment_id: int):
    items = []
    payment = Payment.objects.get(pk=payment_id)
    booking = payment.booking.all().select_related("seat")
    for book in booking:
        product = stripe.Product.create(name=f"{book.seat.number} {book.seat.seat_class}")
        price = stripe.Price.create(product=product.id, unit_amount=(book.seat.price * 100), currency="usd")
        item = {"price": price.id, "quantity": 1}
        items.append(item)

    return items

