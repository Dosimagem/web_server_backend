import pytest

from web_server.service.forms import SegmentationAnalysisCreateForm


def test_create_form(segmentation_analysis_info, segmentation_analysis_file):

    form = SegmentationAnalysisCreateForm(data=segmentation_analysis_info, files=segmentation_analysis_file)

    assert form.is_valid()


@pytest.mark.parametrize(
    'field',
    [
        'order',
        'images',
        'analysis_name',
    ],
)
def test_missing_fields(field, segmentation_analysis_info, segmentation_analysis_file):

    segmentation_analysis_file.pop(field) if field == 'images' else segmentation_analysis_info.pop(field)

    form = SegmentationAnalysisCreateForm(data=segmentation_analysis_info, files=segmentation_analysis_file)

    assert not form.is_valid()

    assert form.errors == {field: ['Este campo é obrigatório.']}


def test_invalid_order_of_wrong_service(clinic_order, segmentation_analysis_info, segmentation_analysis_file):

    segmentation_analysis_info['order'] = clinic_order

    form = SegmentationAnalysisCreateForm(data=segmentation_analysis_info, files=segmentation_analysis_file)

    assert not form.is_valid()

    assert form.errors == {'__all__': ['Este serviço não foi contratado nesse pedido.']}


def test_invalid_create_form_analysis_name_must_be_unique_per_order(
    segmentation_analysis, segmentation_analysis_info, segmentation_analysis_file
):

    form = SegmentationAnalysisCreateForm(data=segmentation_analysis_info, files=segmentation_analysis_file)

    assert not form.is_valid()

    assert form.errors == {'__all__': ['Análise de Segmentação com este Order e Nome da análise já existe.']}


def test_invalid_analysis_name_length_must_least_3(segmentation_analysis_info, segmentation_analysis_file):

    segmentation_analysis_info['analysis_name'] = '2'

    form = SegmentationAnalysisCreateForm(data=segmentation_analysis_info, files=segmentation_analysis_file)

    assert not form.is_valid()

    expected = ['Certifique-se de que o valor tenha no mínimo 3 caracteres (ele possui 1).']

    assert form.errors == {'analysis_name': expected}
