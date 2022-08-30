from rest_framework.authentication import TokenAuthentication


class MyTokenAuthentication(TokenAuthentication):
    keyword = 'Bearer'


def user_to_dict(user):
    return dict(
        name=user.profile.name,
        phone=user.profile.phone,
        role=user.profile.role,
        institution=user.profile.institution,
        email=user.email
    )


def list_errors(errors):

    list_ = []

    for field_name, field_errors in errors.items():
        for error in field_errors:
            if error == 'This field is required.':
                msg = field_name.capitalize() + ' field is required.'
                list_.append(msg)
            else:
                list_.append(error)

    return list_
