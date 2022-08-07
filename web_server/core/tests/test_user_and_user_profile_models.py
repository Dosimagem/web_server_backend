from django.contrib.auth import get_user_model

from web_server.core.models import UserProfile


User = get_user_model()


def test_create_user_profile(user):
    assert UserProfile.objects.exists()


def test_str(user):
    assert str(user.profile) == user.profile.name


def test_delete_user_profile_not_delete_user(user):
    profile = user.profile
    profile.delete()
    assert not UserProfile.objects.exists()
    assert User.objects.exists()


def test_delete_user_delete_user_profile(user):
    user.delete()
    assert not UserProfile.objects.exists()
    assert not User.objects.exists()


def test_user_get_name(user):
    assert user.get_name() == user.profile.name


def test_user_first_name(user):
    user.profile.name = 'Name Surname'
    assert user.get_first_name() == 'Name'


def test_user_first_name_for_user_without_name(user):
    user.profile.name = None
    assert user.get_first_name() == 'This user have not a name'
