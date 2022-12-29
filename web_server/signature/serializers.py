from rest_framework import serializers

from web_server.signature.models import Benefit, Signature


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
