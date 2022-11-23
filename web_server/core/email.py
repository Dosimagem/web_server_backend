from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string

User = get_user_model()


DOSIMAGEM_EMAIL = settings.DEFAULT_FROM_EMAIL
FRONT_DOMAIN = settings.FRONT_DOMAIN


def _jwt_verification_email_secret(user):
    jwt_payload = {'id': str(user.uuid), 'exp': datetime.now(tz=timezone.utc) + timedelta(seconds=24 * 60 * 60)}
    return jwt.encode(jwt_payload, settings.SECRET_KEY)


def send_email_verification(user):

    token = _jwt_verification_email_secret(user)
    email = user.email
    context = {'link': f'{FRONT_DOMAIN}/users/{user.uuid}/email-confirm/?token={token}'}
    body = render_to_string('core/email_verify.txt', context)
    send_mail('Verificação de email da sua conta Dosimagem', body, DOSIMAGEM_EMAIL, [email])

    user.verification_email_secret = token
    user.sent_verification_email = True
    user.email_verified = False
    user.save()
