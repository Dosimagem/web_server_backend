from rest_framework.authentication import TokenAuthentication


class MyTokenAuthentication(TokenAuthentication):
    keyword = 'Bearer'


def list_errors(errors):

    list_ = []

    for field_name, field_errors in errors.items():
        for error in field_errors:
            if error == 'This field is required.':
                name = field_name.capitalize()
                msg = error.replace('This', name)
                list_.append(msg)
            elif error == 'Ensure this value is greater than or equal to 0.0.':
                name = field_name.capitalize()
                msg = error.replace('this', name)
                list_.append(msg)
            else:
                list_.append(error)

    return list_
