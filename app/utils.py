from io import BytesIO

import stripe
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from trips.models import Seat


def generate_ticket_pdf(data: dict) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    x = 100
    y = 750
    for name, value in data.items():
        c.drawString(x, y, f"{name}: {value}")
        y -= 25
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def generate_seats_map(seats: list) -> dict:
    seat_map = {"business": {}, "economy": {}}
    for seat in seats:
        row_number = int(seat.number[:-1])
        if seat.seat_class == "business":
            if row_number not in seat_map["business"]:
                seat_map["business"][row_number] = []
            seat_map["business"][row_number].append(seat)
        else:
            if row_number not in seat_map["economy"]:
                seat_map["economy"][row_number] = []
            seat_map["economy"][row_number].append(seat)

    return seat_map


def generate_items_for_payment(stripe: stripe, seats: Seat, payment_id: int) -> list:
    items = []

    for seat in seats:
        product = stripe.Product.create(
            name=f"{seat.number} {seat.seat_class}", metadata={"payment_id": payment_id}
        )
        price = stripe.Price.create(
            product=product.id,
            unit_amount=(seat.price * 100),
            currency="usd",
            metadata={"payment_id": payment_id},
        )
        item = {"price": price.id, "quantity": 1}
        items.append(item)

    return items


def create_checkout_session(
    stripe: stripe, domain_url: str, seats: list, payment_id: int
) -> str:
    """
    Creates items(tickets) for the  Stripe dashboard
    Creates checkout session for the payment
    """
    items = generate_items_for_payment(stripe, seats, payment_id)

    checkout_session = stripe.checkout.Session.create(
        success_url=domain_url
        + f"success/{payment_id}"
        + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=domain_url + "cancelled/",
        payment_method_types=["card"],
        metadata={"payment_id": payment_id},
        mode="payment",
        expires_at=int((timezone.now() + timezone.timedelta(minutes=30)).timestamp()),
        line_items=items,
    )
    return checkout_session.id
