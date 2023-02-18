import pytest
from django.db.utils import IntegrityError

from web_server.isotope.models import Isotope


def test_model_isotope_create(lu_177):
    assert Isotope.objects.exists()


def test_isotope_str(lu_177):
    assert str(lu_177) == 'Lu-177'


def test_isotopename_must_be_unique(lu_177):

    with pytest.raises(IntegrityError):
        Isotope.objects.create(name='Lu-177')


def test_default(db):

    isotope = Isotope.objects.create(name='Y-90')

    assert not isotope.dosimetry
    assert not isotope.radiosyno
