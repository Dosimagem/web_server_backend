from django.contrib.auth import get_user_model
from web_server.core.models import UserProfile


User = get_user_model()


def test_created_user_profile_when_user(user_info, db):
    user = User.objects.create(**user_info)
    assert UserProfile.objects.exists()
    assert UserProfile.objects.first().user_id == user.id
