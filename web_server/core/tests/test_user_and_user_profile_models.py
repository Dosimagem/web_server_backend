from django.contrib.auth import get_user_model

from web_server.core.models import UserProfile

User = get_user_model()


def test_create_user_profile(user):
    assert UserProfile.objects.exists()


def test_str(user):
    assert str(user.profile) == user.profile.clinic


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


def test_cnpj_mask(user):
    assert user.profile._cnpj_mask() == '42.438.610/0001-11'


def test_cpf_mask(user):
    assert user.profile._cpf_mask() == '937.438.511-21'


def test_default_value_user(db):
    user = User.objects.create(email='user1@email.com')

    assert not user.email_verified
    assert not user.is_staff
    assert user.is_active
    assert not user.sent_verification_email
