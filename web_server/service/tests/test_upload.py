from unittest import mock

from web_server.service.models import upload_img_to, upload_report_to, _normalize_email


def test_normalize_email(user):
    assert 'test_email_com' == _normalize_email(user.email)


@mock.patch('web_server.service.models.now')
def test_upload_name_images_dosimetry_order(mock, dosimetry_clinical_order, datetime_now):
    t, date, time = datetime_now

    mock.return_value = t

    user = _normalize_email(dosimetry_clinical_order.requester.email)

    assert upload_img_to(dosimetry_clinical_order, filename='filename.zip') == f'{user}/images/{date}/images_{time}.zip'


@mock.patch('web_server.service.models.now')
def test_upload_name_report_dosimetry_order(mock, dosimetry_clinical_order, datetime_now):
    t, date, time = datetime_now

    mock.return_value = t
    user = _normalize_email(dosimetry_clinical_order.requester.email)

    assert upload_report_to(dosimetry_clinical_order, 'filename.pdf') == f'{user}/report/{date}/report_{time}.pdf'


@mock.patch('web_server.service.models.now')
def test_upload_name_images_segmentantion_order(mock, segmentantion_order, datetime_now):
    t, date, time = datetime_now

    mock.return_value = t

    user = _normalize_email(segmentantion_order.requester.email)

    assert upload_img_to(segmentantion_order, filename='filename.zip') == f'{user}/images/{date}/images_{time}.zip'


@mock.patch('web_server.service.models.now')
def test_upload_name_report_segmentantion_order(mock, segmentantion_order, datetime_now):
    t, date, time = datetime_now

    mock.return_value = t
    user = _normalize_email(segmentantion_order.requester.email)

    assert upload_report_to(segmentantion_order, 'filename.pdf') == f'{user}/report/{date}/report_{time}.pdf'
