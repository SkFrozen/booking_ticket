from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from requests import delete

from .models import Booking, Payment
from .utils import generate_ticket_pdf

User = get_user_model()


@shared_task
def reject_booking_task(payment_id: int) -> None:
    print("reject_task")
    payment = Payment.objects.get(pk=payment_id)

    if not payment.paid:
        booking = payment.booking.all().select_related("seat", "passport")
        for book in booking:
            book.seat.is_booked = False
            book.seat.save()
            if not book.passport.owner:
                print("passport deleted")
                book.passport.delete()
            else:
                print("book deleted")
                book.delete()
        payment.delete()
        print("payment deleted")


@shared_task
def send_ticket_to_user(payment_id: id, email: str) -> None:
    payment = Payment.objects.get(pk=payment_id)
    booking = payment.booking.all()
    tickets = []
    try:
        for book in booking:
            ticket = generate_ticket_pdf(book.ticket)
            tickets.append(ticket)
        subject = "Here is your ticket!"
        message = f"Hello. You can download and print the ticket"
        send_email_task(message, email, subject, tickets, "ticket")
    except Exception as e:
        print(e)


def send_email_task(
    message: str,
    email: str,
    subject: str,
    files: list | None = None,
    file_name: str = "file",
    file_ext: str = "pdf",
    file_content: str = "application/pdf",
) -> None:
    """
    Send email with file attachment
    """
    print(f"sending email '{email}', '{subject}', '{message}'")

    if not email or not message:
        return

    mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [email])

    if files is not None:
        for k, file in enumerate(files):
            file_name = f"{file_name}_{k}.{file_ext}"
            mail.attach(file_name, file, file_content)

    mail.send()
