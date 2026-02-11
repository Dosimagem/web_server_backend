from rest_framework import serializers


class ContactSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    role = serializers.CharField(max_length=30)
    company = serializers.CharField(max_length=30)
    number = serializers.CharField(max_length=30)
    subject = serializers.CharField(max_length=200)
    message = serializers.CharField(max_length=1000)
