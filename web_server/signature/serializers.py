from django.db import transaction
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.fields import to_choices_dict

from web_server.signature.models import Benefit, Signature
from web_server.signature.service_layer import new_test_period


class ModalityField(serializers.ChoiceField):
    default_error_messages = {'invalid_choice': _('"{input}" is not a valid modality.')}

    def _get_choices(self):
        return super()._get_choices()

    def _set_choices(self, choices):
        self._choices = to_choices_dict(choices)

        self.choice_strings_to_values = {str(value): key for key, value in self.choices.items()}

    choices = property(_get_choices, _set_choices)


class BenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefit
        fields = ('uuid', 'name', 'uri')
        read_only_fields = ('uuid', 'name', 'uri')


class SignatureSerializer(serializers.ModelSerializer):

    benefits = BenefitSerializer(many=True, read_only=True)
    modality = serializers.CharField(source='get_modality_display')
    bill_url = serializers.SerializerMethodField()

    class Meta:
        model = Signature
        fields = (
            'uuid',
            'plan',
            'price',
            'modality',
            'discount',
            'benefits',
            'hired_period',
            'test_period',
            'activated',
            'bill_url',
        )
        read_only_fields = (
            'uuid',
            'plan',
            'price',
            'modality',
            'discount',
            'benefits',
            'hired_period',
            'test_period',
            'activated',
        )

    def get_bill_url(self, obj):
        request = self.context.get('request')
        if obj.bill.name and request:
            return request.build_absolute_uri(obj.bill.url)
        return None


class SignatureCreateSerizaliser(serializers.ModelSerializer):

    trial_time_error = _('Not a valid trial period. Example: 30 days.')

    benefits = serializers.ListField()
    trial_time = serializers.CharField()
    modality = ModalityField(choices=Signature.Modality.choices, required=False)

    class Meta:
        model = Signature
        fields = ('plan', 'modality', 'trial_time', 'benefits', 'discount', 'price')

    def validate_trial_time(self, value):
        """
        Must be some like '30 days'
        """

        try:
            day, period = value.split()
        except ValueError:
            raise serializers.ValidationError(self.trial_time_error)

        if period != 'days':
            raise serializers.ValidationError(self.trial_time_error)

        try:
            value = int(day)
        except ValueError:
            raise serializers.ValidationError(self.trial_time_error)

        return value

    def validate_benefits(self, value):
        try:
            for ben in value:
                Benefit.objects.get(name=ben)
        except Benefit.DoesNotExist:
            raise serializers.ValidationError(_('The benefit %(ben)s is not registered.' % ({'ben': ben})))
        return value

    def create(self, validated_data):

        range_test_period = new_test_period(validated_data['trial_time'])
        data = {**validated_data, 'activated': True, **range_test_period}
        data.pop('benefits')
        data.pop('trial_time')
        signature = Signature(**data)

        with transaction.atomic():
            signature.save()
            list_benefits = validated_data['benefits']
            signature.benefits.set(Benefit.objects.get(name=ben) for ben in list_benefits)

        return signature
