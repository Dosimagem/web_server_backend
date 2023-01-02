from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string

User = get_user_model()


DOSIMAGEM_EMAIL = settings.DEFAULT_FROM_EMAIL
FRONT_DOMAIN = settings.FRONT_DOMAIN
EMAIL_TOKEN_LIFETIME = settings.EMAIL_TOKEN_LIFETIME


def _jwt_verification_email_secret(user):
    jwt_payload = {'id': str(user.uuid), 'exp': datetime.now(tz=timezone.utc) + timedelta(seconds=EMAIL_TOKEN_LIFETIME)}
    return jwt.encode(jwt_payload, settings.SIGNING_KEY)


def send_email_verification(user):

    token = _jwt_verification_email_secret(user)
    email = user.email
    context = {'link': f'{FRONT_DOMAIN}/users/{user.uuid}/email-confirm/?token={token}'}
    body_txt = render_to_string('core/email_verify.txt', context)
    body_html = render_to_string('core/email_verify.html', context)
    send_mail('Verificação de email da sua conta Dosimagem', body_txt, DOSIMAGEM_EMAIL, [email], html_message=body_html)

    user.verification_email_secret = token
    user.sent_verification_email = True
    user.email_verified = False
    user.save()


def send_reset_password(user):

    token = _jwt_verification_email_secret(user)
    email = user.email
    context = {'link': f'{FRONT_DOMAIN}/users/{user.uuid}/reset-password/?token={token}'}
    body_txt = render_to_string('core/reset_password.txt', context)
    body_html = render_to_string('core/reset_password.html', context)
    send_mail('Dosimagem - Resetando a senha', body_txt, DOSIMAGEM_EMAIL, [email], html_message=body_html)

    user.reset_password_secret = token
    user.sent_reset_password_email = True
    user.save()
