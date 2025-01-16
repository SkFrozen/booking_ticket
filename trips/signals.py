from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Country


@receiver(post_save, sender=Country)
@receiver(post_delete, sender=Country)
def clear_country_cache(sender, **kwargs):
    cache.delete("countries")
