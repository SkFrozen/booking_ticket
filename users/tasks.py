from celery import shared_task
from django.contrib.auth import get_user_model

from .email import ConfirmUserRegisterEmailSender

User = get_user_model()


@shared_task(ignore_result=True)
def delete_user_task(user_id: int):
    print("task: delete_user()=", user_id)
    User.objects.filter(id=user_id, is_active=False).delete()


@shared_task(max_retries=3, autoretry_for=(Exception,))
def send_register_email_task(domain: str, user_id: int):
    print("task: send_register_email()=", domain, user_id)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        pass
    else:
        ConfirmUserRegisterEmailSender(domain, user).send_mail()
        return True

    return False
