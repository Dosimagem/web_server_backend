import pytest


@pytest.fixture
def form_data(calibration_infos, calibration_file):  # TODO change name for first_http_data_calibration

    return {
         'isotope': calibration_infos['isotope'].name,
         'calibrationName': calibration_infos['calibration_name'],
         'syringeActivity': calibration_infos['syringe_activity'],
         'residualSyringeActivity': calibration_infos['residual_syringe_activity'],
         'measurementDatetime': calibration_infos['measurement_datetime'],
         'phantomVolume': calibration_infos['phantom_volume'],
         'acquisitionTime': calibration_infos['acquisition_time'],
         'images': calibration_file['images']
    }


@pytest.fixture
def second_form_data(second_calibration_infos, calibration_file):  # TODO change name for second_http_data_calibration
    return {
         'isotope': second_calibration_infos['isotope'].name,
         'calibrationName': second_calibration_infos['calibration_name'],
         'syringeActivity': second_calibration_infos['syringe_activity'],
         'residualSyringeActivity': second_calibration_infos['residual_syringe_activity'],
         'measurementDatetime': second_calibration_infos['measurement_datetime'],
         'phantomVolume': second_calibration_infos['phantom_volume'],
         'acquisitionTime': second_calibration_infos['acquisition_time'],
         'images': calibration_file['images']
    }


@pytest.fixture
def form_data_clinic_dosimetry(clinic_dosimetry_info, clinic_dosimetry_file):

    return {
         'calibrationId': clinic_dosimetry_info['calibration'].uuid,
         'images': clinic_dosimetry_file['images'],
         'analysisName': clinic_dosimetry_info['analysis_name'],
         'injectedActivity': clinic_dosimetry_info['injected_activity'],
         'administrationDatetime': clinic_dosimetry_info['administration_datetime'],

    }


@pytest.fixture
def form_data_preclinic_dosimetry(preclinic_dosimetry_info, preclinic_dosimetry_file):

    return {
         'calibrationId': preclinic_dosimetry_info['calibration'].uuid,
         'images': preclinic_dosimetry_file['images'],
         'analysisName': preclinic_dosimetry_info['analysis_name'],
         'injectedActivity': preclinic_dosimetry_info['injected_activity'],
         'administrationDatetime': preclinic_dosimetry_info['administration_datetime'],
    }
