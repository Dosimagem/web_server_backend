from rest_framework import serializers


class GeneralBudgetSerilizer(serializers.Serializer):
    service = serializers.CharField(max_length=30)
    treatment_type = serializers.CharField(max_length=60)
    number_of_samples = serializers.IntegerField(min_value=0)
    frequency = serializers.IntegerField(min_value=0)
    comments = serializers.CharField(max_length=100000)


class CompModelBudgetSerilizer(serializers.Serializer):
    service = serializers.CharField(max_length=30)
    research_line = serializers.CharField(max_length=60)
    project_description = serializers.CharField(max_length=100000)
