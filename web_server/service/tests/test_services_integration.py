from web_server.notification.models import Notification
from web_server.service.models import Calibration, ClinicDosimetryAnalysis, Order


def test_create_analysis(clinic_dosimetry_info, clinic_dosimetry_file):

    analysis = ClinicDosimetryAnalysis.objects.create(
        **clinic_dosimetry_info, **clinic_dosimetry_file, status=ClinicDosimetryAnalysis.Status.ANALYZING_INFOS
    )

    notification = Notification.objects.last()

    assert f'Analise {analysis.code} criada.' == notification.message
    assert not notification.checked
    assert Notification.Kind.SUCCESS.label == notification.get_kind_display()


def test_delete_analysis(clinic_dosimetry_info, clinic_dosimetry_file):

    analysis = ClinicDosimetryAnalysis.objects.create(
        **clinic_dosimetry_info, **clinic_dosimetry_file, status=ClinicDosimetryAnalysis.Status.ANALYZING_INFOS
    )

    analysis.delete()

    notification = Notification.objects.last()

    assert f'Analise {analysis.code} deletada.' == notification.message
    assert not notification.checked
    assert Notification.Kind.SUCCESS.label == notification.get_kind_display()


def test_update_analysis(clinic_dosimetry_info, clinic_dosimetry_file):

    analysis = ClinicDosimetryAnalysis.objects.create(
        **clinic_dosimetry_info, **clinic_dosimetry_file, status=ClinicDosimetryAnalysis.Status.ANALYZING_INFOS
    )

    analysis.status = ClinicDosimetryAnalysis.Status.DATA_SENT

    analysis.save()

    notification = Notification.objects.last()

    assert f'Analise {analysis.code} atualizada.' == notification.message
    assert not notification.checked
    assert Notification.Kind.SUCCESS.label == notification.get_kind_display()


def test_create_calibration(calibration_infos):

    cali = Calibration.objects.create(**calibration_infos)

    notification = Notification.objects.last()

    assert f'{cali.calibration_name} criada com sucesso.' == notification.message
    assert not notification.checked
    assert Notification.Kind.SUCCESS.label == notification.get_kind_display()


def test_delete_calibration(calibration_infos):

    cali = Calibration.objects.create(**calibration_infos)

    cali.delete()

    notification = Notification.objects.last()

    assert f'{cali.calibration_name} deletada com sucesso.' == notification.message
    assert not notification.checked
    assert Notification.Kind.SUCCESS.label == notification.get_kind_display()


def test_update_calibration(calibration_infos):

    cali = Calibration.objects.create(**calibration_infos)

    cali.phantom_volume = 555.3

    cali.save()

    notification = Notification.objects.last()

    assert f'{cali.calibration_name} atualizada com sucesso.' == notification.message
    assert not notification.checked
    assert Notification.Kind.SUCCESS.label == notification.get_kind_display()


def test_create_order(create_order_data):

    order = Order.objects.create(**create_order_data)

    notification = Notification.objects.last()

    assert f'Pedido {order.code} criado.' == notification.message
    assert not notification.checked
    assert Notification.Kind.SUCCESS.label == notification.get_kind_display()


def test_update_order(create_order_data):

    order = Order.objects.create(**create_order_data)

    order.status_payment = Order.PaymentStatus.CONFIRMED
    order.save()

    notification = Notification.objects.last()

    assert f'Pedido {order.code} atualizado.' == notification.message
    assert not notification.checked
    assert Notification.Kind.SUCCESS.label == notification.get_kind_display()
