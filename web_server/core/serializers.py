from django.contrib.auth import get_user_model, password_validation
from django.utils.translation import gettext as _
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField


User = get_user_model()


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField()


class ResetPasswordConfirmSerializer(serializers.Serializer):

    token = serializers.CharField()
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': _("The two password fields didn't match.")})

        user = self.instance
        password_validation.validate_password(data['new_password1'], user)

        return data


class ChangePasswordSerializer(serializers.ModelSerializer):

    old_password = serializers.CharField(max_length=128)
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': _("The two password fields didn't match.")})

        user = self.instance
        password_validation.validate_password(data['new_password1'], user)

        return data

    def validate_old_password(self, value):
        user = self.instance
        if not user.check_password(value):
            raise serializers.ValidationError('Password antigo não está correto.')
        return value


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PhoneSerializer(serializers.Serializer):
    phone = PhoneNumberField()
