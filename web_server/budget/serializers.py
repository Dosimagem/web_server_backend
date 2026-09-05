from rest_framework import serializers

from web_server.service.models import Order

LIST = [e.label for e in Order.ServicesName] + ['Modelagem Computacional']   # TODO: Resolver isso


class GeneralBudgetSerializer(serializers.Serializer):
    service = serializers.ChoiceField(choices=LIST)


class BaseClinicBudgetSerializer(serializers.Serializer):
    treatment_type = serializers.CharField(max_length=60)
    number_of_patients = serializers.IntegerField(min_value=0)
    frequency = serializers.CharField(max_length=60, required=False)
    comments = serializers.CharField(max_length=100000)


class ClinicDosimetryBudgetSerializer(BaseClinicBudgetSerializer):
    equipment_type = serializers.ChoiceField(choices=['SPECT', 'PET'])
    equipment_modality = serializers.ChoiceField(choices=['SPECT', 'SPECT_CT', 'SPECT_MRI', 'PET', 'PET_CT', 'PET_MRI'])

    def validate(self, attrs):
        eq_type = attrs.get('equipment_type')
        eq_mod = attrs.get('equipment_modality')
        if eq_type == 'SPECT' and eq_mod not in ['SPECT', 'SPECT_CT', 'SPECT_MRI']:
            raise serializers.ValidationError(
                {'equipment_modality': 'A modalidade do equipamento deve ser SPECT, SPECT_CT ou SPECT_MRI se o tipo for SPECT.'}
            )
        if eq_type == 'PET' and eq_mod not in ['PET', 'PET_CT', 'PET_MRI']:
            raise serializers.ValidationError(
                {'equipment_modality': 'A modalidade do equipamento deve ser PET, PET_CT ou PET_MRI se o tipo for PET.'}
            )
        return attrs


class PreClinicDosimetryBudgetSerializer(serializers.Serializer):
    research_line = serializers.CharField(max_length=60)
    number_of_patients = serializers.IntegerField(min_value=0)
    frequency = serializers.CharField(max_length=60, required=False)
    comments = serializers.CharField(max_length=100000)


class SegmentantioQuantificationSerialier(BaseClinicBudgetSerializer):
    ...


class RadiosinoSerialier(BaseClinicBudgetSerializer):
    ...


class CompModelBudgetSerilizer(serializers.Serializer):
    research_line = serializers.CharField(max_length=60)
    project_description = serializers.CharField(max_length=100000)
