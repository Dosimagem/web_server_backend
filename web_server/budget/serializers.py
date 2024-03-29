from rest_framework import serializers

from web_server.service.models import Order

LIST = [e.label for e in Order.ServicesName] + ['Modelagem Computacional']   # TODO: Resolver isso


class GeneralBudgetSerializer(serializers.Serializer):
    service = serializers.ChoiceField(choices=LIST)


class ClinicDosimetryBudgetSerializer(serializers.Serializer):
    treatment_type = serializers.CharField(max_length=60)
    number_of_patients = serializers.IntegerField(min_value=0)
    frequency = serializers.CharField(max_length=60, required=False)
    comments = serializers.CharField(max_length=100000)


class PreClinicDosimetryBudgetSerializer(serializers.Serializer):
    research_line = serializers.CharField(max_length=60)
    number_of_patients = serializers.IntegerField(min_value=0)
    frequency = serializers.CharField(max_length=60, required=False)
    comments = serializers.CharField(max_length=100000)


class SegmentantioQuantificationSerialier(ClinicDosimetryBudgetSerializer):
    ...


class RadiosinoSerialier(ClinicDosimetryBudgetSerializer):
    ...


class CompModelBudgetSerilizer(serializers.Serializer):
    research_line = serializers.CharField(max_length=60)
    project_description = serializers.CharField(max_length=100000)
