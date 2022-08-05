def test_user_get_name(user):
    assert user.get_name() == user.profile.name


def test_user_first_name(user):
    user.profile.name = 'Name Surname'
    assert user.get_first_name() == 'Name'


def test_user_first_name_for_user_without_name(user):
    user.profile.name = None
    assert user.get_first_name() == 'This user have not a name'
