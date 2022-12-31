from datetime import timedelta
from pathlib import Path

import dj_database_url
from decouple import Csv, config
from django.conf.locale.pt_BR import formats as pt_BR_formats

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool, default=False)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

AUTH_USER_MODEL = 'core.CustomUser'

# TODO: This may be not make sense in SPA context

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/profile'
LOGOUT_REDIRECT_URL = '/'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    #
    'collectfast',
    #
    'django.contrib.staticfiles',
    #
    'django_extensions',
    'corsheaders',
    #
    'web_server.core',
    'web_server.service',
    'web_server.radiosynoviorthesis',
    'web_server.signature',
    'web_server.budget',
    'web_server.notification',
    #
    'rest_framework',
    #
    'django_cleanup.apps.CleanupConfig',
    'phonenumber_field',
]

MIDDLEWARE = [
    'web_server.core.middleware.HealthCheckMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'web_server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'web_server/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'web_server.wsgi.application'

INTERNAL_IPS = config('INTERNAL_IPS', cast=Csv(), default=[])

if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases


default_db_url = 'sqlite:///' + str(BASE_DIR / 'db.sqlite3')
parse_db = dj_database_url.parse
DATABASES = {'default': config('DATABASE_URL', default=default_db_url, cast=parse_db)}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles/'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles/'

COLLECTFAST_ENABLED = False

AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default=None)

# STORAGE CONFIGURATION IN S3 AWS
# ------------------------------------------------------------------------------

if AWS_ACCESS_KEY_ID:  # pragma: no cover
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_PRELOAD_METADATA = True
    AWS_AUTO_CREATE_BUCKET = False
    AWS_QUERYSTRING_AUTH = True
    AWS_S3_CUSTOM_DOMAIN = None
    AWS_DEFAULT_ACL = 'private'

    COLLECTFAST_STRATEGY = 'collectfast.strategies.boto3.Boto3Strategy'
    COLLECTFAST_ENABLED = True

    # Static Assets
    # ------------------------------------------------------------------------------
    STATICFILES_STORAGE = 's3_folder_storage.s3.StaticStorage'
    STATIC_S3_PATH = 'static'
    STATIC_ROOT = f'/{STATIC_S3_PATH}/'
    STATIC_URL = f'//s3.amazonaws.com/{AWS_STORAGE_BUCKET_NAME}/{STATIC_S3_PATH}/'
    ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

    # Upload Media Folder
    DEFAULT_FILE_STORAGE = 's3_folder_storage.s3.DefaultStorage'
    DEFAULT_S3_PATH = 'media'
    MEDIA_ROOT = f'/{DEFAULT_S3_PATH}/'
    MEDIA_URL = f'//s3.amazonaws.com/{AWS_STORAGE_BUCKET_NAME}/{DEFAULT_S3_PATH}/'

    INSTALLED_APPS.append('s3_folder_storage')
    INSTALLED_APPS.append('storages')


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS config
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default=[], cast=Csv())

# FRONT DOMAIN
FRONT_DOMAIN = config('FRONT_DOMAIN')


# djangorestframework-camel-case

DEFAULT_RENDERER_CLASSES = ['djangorestframework_camel_case.render.CamelCaseJSONRenderer']

if DEBUG:
    DEFAULT_RENDERER_CLASSES.append('djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer')

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': DEFAULT_RENDERER_CLASSES,
    'DEFAULT_PARSER_CLASSES': (
        'djangorestframework_camel_case.parser.CamelCaseFormParser',
        'djangorestframework_camel_case.parser.CamelCaseMultiPartParser',
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
    ),
    'JSON_UNDERSCOREIZE': {
        'no_underscore_before_number': True,
    },
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'web_server.core.auth.MyJWTCookieAuthentication',
    ],
}


# simpleJWT
SIGNING_KEY = config('SIGNING_KEY')

ACCESS_TOKEN_LIFETIME = config('ACCESS_TOKEN_LIFETIME', cast=int, default=15)
REFRESH_TOKEN_LIFETIME = config('REFRESH_TOKEN_LIFETIME', cast=int, default=48 * 60)

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=ACCESS_TOKEN_LIFETIME),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=REFRESH_TOKEN_LIFETIME),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SIGNING_KEY,
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'USER_ID_FIELD': 'uuid',
    'USER_ID_CLAIM': 'id',
}

# dj-rest-auth
REST_AUTH_TOKEN_MODEL = None
JWT_AUTH_COOKIE_USE_CSRF = False
REST_SESSION_LOGIN = False
REST_USE_JWT = True
JWT_AUTH_COOKIE = 'jwt-access-token'
JWT_AUTH_REFRESH_COOKIE = 'jwt-refresh-token'
JWT_AUTH_SECURE = config('JWT_AUTH_SECURE', cast=bool, default=True)
JWT_AUTH_HTTPONLY = True
JWT_AUTH_SAMESITE = 'Lax'
JWT_AUTH_REFRESH_COOKIE_PATH = '/api/v1/users/auth/token/'
JWT_AUTH_IN_BODY = False
ACCOUNT_LOGOUT_ON_GET = True

# Avoid conflict between Admin and React front
SESSION_COOKIE_PATH = '/dosimagem/admin/'


# TODO: Esse aconfiguração per informações importantes da requesições
LOGGER_SQL = config('LOGGER_SQL', default=False, cast=bool)

if LOGGER_SQL:
    LOGGING = {
        'version': 1,
        'formatters': {
            'simple': {'format': '\n---\n%(levelname)s %(message)s\n---\n'},
        },
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'filters': ['require_debug_true'],
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
        },
        'loggers': {
            'django.db.backends': {
                'level': 'DEBUG',
                'handlers': ['console'],
            }
        },
    }

# Configurando o sentry sdk

SENTRY_DSN = config('SENTRY_DSN', default=None)

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True,
    )

pt_BR_formats.DATETIME_FORMAT = 'd/m/Y H:i:s'

# Email configs
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

EMAIL_TOKEN_LIFETIME = config('EMAIL_TOKEN_LIFETIME', default=24 * 60 * 60)
