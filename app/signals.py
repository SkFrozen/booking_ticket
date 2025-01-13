from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Payment
from .tasks import reject_booking_task


@receiver(post_save, sender=Payment)
def post_save_booking(sender, instance, created, **kwargs):

    if created:
        reject_booking_task.apply_async(args=[instance.id], countdown=60 * 20)
