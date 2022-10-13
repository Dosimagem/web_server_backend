import pytest
from django.db.utils import IntegrityError


from web_server.service.models import Isotope


def test_model_create(lu_177):
    assert Isotope.objects.exists()


def test_str(lu_177):
    assert str(lu_177) == 'Lu-177'


def test_isotope_name_must_be_unique(lu_177):

    with pytest.raises(IntegrityError):
        Isotope.objects.create(name='Lu-177')
