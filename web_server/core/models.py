from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from validate_docbr import CNPJ, CPF

from web_server.core.validators import (
    validate_cnpj,
    validate_cpf,
    validate_name_is_alpha,
)


class CreationModificationBase(models.Model):

    created_at = models.DateTimeField(_('Creation Date and Time'), auto_now_add=True)
    modified_at = models.DateTimeField(_('Modificatioin Date and Time'), auto_now=True)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        if not email:
            raise ValueError('The given email username must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    App base User class.
    Email and password are required. Other fields are optional.
    """

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. ' 'Unselect this instead of deleting accounts.'
        ),
    )

    email_verified = models.BooleanField('email_verified', default=False)
    sent_verification_email = models.BooleanField(default=False)
    verification_email_secret = models.TextField(default=None, null=True)

    reset_password_secret = models.TextField(default=None, null=True)
    sent_reset_password_email = models.BooleanField(default=False)

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = False

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_name(self):
        """Return the name for the user."""
        return self.profile.name

    def get_first_name(self):
        """Return the name for the user."""
        name = self.profile.name
        if not name:
            return 'This user have not a name'  # TODO test this
        return name.split()[0]

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def to_dict(self):
        return dict(
            name=self.profile.name,
            phone=self.profile.phone_str,
            role=self.profile.role,
            clinic=self.profile.clinic,
            email=self.email,
            cpf=self.profile._cpf_mask(),
            cnpj=self.profile._cnpj_mask(),
        )

    def __str__(self):
        return self.email

    def email_not_verified(self):
        return not self.email_verified


class UserProfile(CreationModificationBase, models.Model):

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='profile')

    name = models.CharField(_('Name'), max_length=150, validators=[validate_name_is_alpha, MinLengthValidator(3)])
    phone = PhoneNumberField()
    # phone = models.CharField(_('Phone'), max_length=30, validators=[validate_international_phonenumber])

    clinic = models.CharField(_('Clinic'), max_length=30)
    role = models.CharField(_('Role'), max_length=30)
    cpf = models.CharField('CPF', max_length=11, validators=[validate_cpf])
    cnpj = models.CharField('CNPJ', max_length=14, validators=[validate_cnpj])

    def __str__(self):
        return self.clinic

    def _cnpj_mask(self):
        cnpj = CNPJ()
        return cnpj.mask(self.cnpj)

    def _cpf_mask(self):
        cpf = CPF()
        return cpf.mask(self.cpf)

    @property
    def phone_str(self):
        return str(self.phone)
