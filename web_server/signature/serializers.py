from rest_framework import serializers
from django.utils.translation import gettext as _

from web_server.signature.models import Benefit, Signature
from web_server.signature.service_layer import new_test_period


class BenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefit
        fields = ('uuid', 'name', 'uri')
        read_only_fields = ('uuid', 'name', 'uri')


class SignatureByUserSerializer(serializers.ModelSerializer):

    benefits = BenefitSerializer(many=True, read_only=True)

    class Meta:
        model = Signature
        fields = ('uuid', 'name', 'price', 'activated', 'benefits', 'hired_period', 'test_period')
        read_only_fields = ('uuid', 'name', 'price', 'activated', 'benefits', 'hired_period', 'test_period')


class SignatureCreateSerizaliser(serializers.Serializer):

    trial_time_error = _('Not a valid trial period. Example: 30 days.')

    plan = serializers.CharField(max_length=160)
    price = serializers.DecimalField(max_digits=14, decimal_places=2)
    benefits = serializers.ListField()
    trial_time = serializers.CharField()



    def validate_trial_time(self, value):

        day, period = value.split()

        if period != 'days':
            raise serializers.ValidationError(self.trial_time_error)

        try:
            value = int(day)
        except:
            raise serializers.ValidationError(self.trial_time_error)

        return value


    def create(self, validated_data):

        range_test_period = new_test_period(validated_data['trial_time'])

        signature = Signature(
            user=validated_data['user'],
            name=validated_data['plan'],
            price=validated_data['price'],
            **range_test_period,
            activated=True
        )

        signature.save()

        list_benefits = validated_data['benefits']
        signature.benefits.set(Benefit.objects.get(name=ben) for ben in list_benefits)

        return signature
