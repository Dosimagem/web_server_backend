from web_server.service.models import Isotope


def test_model_create(lu_177):
    assert Isotope.objects.exists()


def test_str(lu_177):
    assert str(lu_177) == 'Lu-177'
