from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product
from .recommendations import invalidate_similarity_cache


@receiver(post_save, sender=Product)
def clear_cache_on_save(sender, instance, **kwargs):
    invalidate_similarity_cache(instance.pk)


@receiver(post_delete, sender=Product)
def clear_cache_on_delete(sender, instance, **kwargs):
    invalidate_similarity_cache(instance.pk)
