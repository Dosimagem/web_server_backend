from django.contrib.auth import get_user_model
from web_server.core.models import UserProfile


User = get_user_model()


def test_signal_user_have_profile_field_after_save(user_info, db):

    user = User(**user_info)

    assert not hasattr(user, 'profile')

    user.save()

    assert hasattr(user, 'profile')


def test_signal_superuser_must_not_have_profile_after_save(user_info, db):

    user = User.objects.create_superuser(**user_info)

    assert not hasattr(user, 'profile')


def test_signal_staff_user_must_not_have_profile_after_save(user_info, db):

    user = User.objects.create(**user_info, is_staff=True)

    assert not hasattr(user, 'profile')


def test_created_user_profile_when_user(user_info, db):
    user = User.objects.create(**user_info)
    assert UserProfile.objects.exists()
    assert UserProfile.objects.first().user_id == user.id
