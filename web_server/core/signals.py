from django.contrib.auth import get_user_model
from web_server.core.models import UserProfile
from django.db.models.signals import post_save
from django.dispatch import receiver


User = get_user_model()


def _is_backoffice(user):
    return user.is_staff or user.is_superuser


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if _is_backoffice(instance):
        return
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if _is_backoffice(instance):
        return
    if hasattr(instance, 'profile'):
        instance.profile.save()
