from web_server.core.forms import UpdateEmailForm


def test_update_email_success(user):

    email_new = 'user1_new@email.com'

    form = UpdateEmailForm({'email': email_new}, instance=user)

    assert form.is_valid()


def test_fail_invalid_email(user):

    email_new = 'user1#email.com'

    form = UpdateEmailForm({'email': email_new}, instance=user)

    assert not form.is_valid()

    assert {'email': ['Insira um endereço de email válido.']} == form.errors


def test_fail_email_must_be_unique(user, second_user):

    email_new = second_user.email

    form = UpdateEmailForm({'email': email_new}, instance=user)

    assert not form.is_valid()

    assert {'email': ['Usuário com este Endereço de email já existe.']} == form.errors


def test_save(user):

    email_new = 'user1_new@email.com'

    form = UpdateEmailForm({'email': email_new}, instance=user)

    form.full_clean()

    form.save()

    user.refresh_from_db()

    assert email_new == user.email
