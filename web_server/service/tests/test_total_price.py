from decimal import Decimal


def test_set_total_price_only_first_time(dosimetry_clinical_order, dosimetry_clinical_service):
    assert dosimetry_clinical_order.total_price == Decimal('3710.42')

    dosimetry_clinical_service.unit_price = Decimal('1000.00')
    dosimetry_clinical_service.save()
    dosimetry_clinical_order.save()

    assert dosimetry_clinical_order.total_price == Decimal('3710.42')
