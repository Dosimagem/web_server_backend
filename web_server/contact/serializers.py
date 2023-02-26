from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers


class ContactSerializer(serializers.Serializer):

    full_name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    role = serializers.CharField(max_length=30)
    clinic = serializers.CharField(max_length=30)
    phone = PhoneNumberField()
    subject = serializers.CharField(max_length=200)
    message = serializers.CharField(max_length=1000)
