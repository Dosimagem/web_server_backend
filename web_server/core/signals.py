from django.contrib.auth import get_user_model
from web_server.core.models import UserProfile
from django.db.models.signals import post_save
from django.dispatch import receiver


User = get_user_model()


def disable_for_loaddata(signal_handler):
    from functools import wraps

    """
    Decorator that turns off signal handlers when loading fixture data.
    """

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get('raw'):
            return
        signal_handler(*args, **kwargs)
    return wrapper


def _is_backoffice(user):
    return user.is_staff or user.is_superuser


@receiver(post_save, sender=User)
@disable_for_loaddata
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
        # save_profile(instance, **kwargs)
        instance.profile.save()
