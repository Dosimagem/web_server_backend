from web_server.core.models import CostumUser


def test_user_get_name(user_form):
    user = CostumUser.objects.create(name='Name Surname')

    assert user.get_name() == 'Name Surname'


def test_user_first_name(user_form):
    user = CostumUser.objects.create(name='Name Surname')

    assert user.get_first_name() == 'Name'


def test_user_first_name_for_user_without_name(user_form):
    user = CostumUser.objects.create()

    assert user.get_first_name() == 'This user have not a name'
