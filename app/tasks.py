from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage

from .models import Booking
from .utils import generate_ticket_pdf

User = get_user_model()


@shared_task
def send_ticket_to_user(booking_id: int, user_id: int) -> None:

    try:
        booking = Booking.objects.get(id=booking_id)
        user = User.objects.get(id=user_id)
        ticket = generate_ticket_pdf(booking.ticket)
        subject = f"{user.first_name} {user.last_name}'s ticket!"
        message = f"Hello, {user.username}. You can download and print the ticket"
        send_email_task(message, user.email, subject, ticket, "ticket.pdf")
    except Exception as e:
        print(e)


def send_email_task(
    message: str,
    email: str,
    subject: str,
    file: bytes | None = None,
    file_name: str = "file.pdf",
    file_content: str = "application/pdf",
) -> None:
    """
    Send email with file attachment
    """
    print(f"sending email '{email}', '{subject}', '{message}'")

    if not email or not message:
        return

    mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [email])
    if file:
        mail.attach(file_name, file, file_content)
    mail.send()
