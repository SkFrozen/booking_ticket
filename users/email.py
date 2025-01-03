from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import User


class BaseEmailSender:
    template_name = None
    subject = None
    user_id_field = "pk"

    def __init__(self, domain: str, user: User):
        self._domain = domain
        self._user = user

    def get_template_name(self) -> str:
        if self.template_name is None:
            raise NotImplementedError("template_name is not defined")
        return self.template_name

    def get_subject(self) -> str:
        if self.subject is None:
            raise NotImplementedError("subject is not defined")
        return self.subject

    def send_mail(self):
        mail = EmailMultiAlternatives(
            subject=self.get_subject() + " on site " + self._domain,
            to=[self._user.email],
        )
        mail.attach_alternative(self._get_mail_body(), "text/html")
        mail.send()

    def _get_mail_body(self) -> str:
        context = {
            "user": self._user,
            "domain": self._domain,
            "uidb64": self._get_user_base64(),
            "token": self._get_token(),
        }
        return render_to_string(self.get_template_name(), context)

    def _get_token(self) -> str:
        return default_token_generator.make_token(self._user)

    def _get_user_base64(self) -> str:
        return urlsafe_base64_encode(
            force_bytes(getattr(self._user, self.user_id_field))
        )


class ConfirmUserRegisterEmailSender(BaseEmailSender):
    template_name = "registration/email_confirm.html"
    user_id_field = "username"
    subject = "Confirm registration"
