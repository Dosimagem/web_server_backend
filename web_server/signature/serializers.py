from rest_framework import serializers
from django.utils.translation import gettext as _
from django.db import transaction

from web_server.signature.models import Benefit, Signature
from web_server.signature.service_layer import new_test_period


class BenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefit
        fields = ('uuid', 'name', 'uri')
        read_only_fields = ('uuid', 'name', 'uri')


class SignatureByUserSerializer(serializers.ModelSerializer):

    benefits = BenefitSerializer(many=True, read_only=True)
    modality = serializers.CharField(source="get_modality_display")

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



class SignatureCreateSerizaliser(serializers.ModelSerializer):

    trial_time_error = _('Not a valid trial period. Example: 30 days.')

    benefits = serializers.ListField()
    trial_time = serializers.CharField()
    modality = serializers.CharField()


    class Meta:
        model = Signature
        fields = ('plan', 'modality', 'trial_time', 'benefits', 'discount', 'price')


    def validate_trial_time(self, value):

        day, period = value.split()

        if period != 'days':
            raise serializers.ValidationError(self.trial_time_error)

        try:
            value = int(day)
        except:
            raise serializers.ValidationError(self.trial_time_error)

        return value

    def validate_benefits(self, value):
        try:
            [Benefit.objects.get(name=ben) for ben in value]
        except Benefit.DoesNotExist:
            raise serializers.ValidationError(_('Benefit not registered.'))
        return value

    def validate(self, attrs):

        value = attrs['modality'].upper()
        for choice in Signature.Modality:
             if value == choice.name:
                attrs['modality'] = choice.value

        return attrs


    def create(self, validated_data):

        range_test_period = new_test_period(validated_data['trial_time'])
        data = {**validated_data, "activated": True, **range_test_period}
        data.pop('benefits')
        data.pop('trial_time')
        signature = Signature(**data)

        with transaction.atomic():
            signature.save()
            list_benefits = validated_data['benefits']
            signature.benefits.set(Benefit.objects.get(name=ben) for ben in list_benefits)

        return signature
