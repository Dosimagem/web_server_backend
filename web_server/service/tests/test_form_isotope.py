from web_server.service.forms import IsotopeForm


def test_valid(lu_177):

    form = IsotopeForm({'isotope': 'Lu-177'})

    assert form.is_valid()


def test_invalid_by_not_registered(lu_177):

    form = IsotopeForm({'isotope': 'Lu-17'})

    assert not form.is_valid()

    assert form.errors == {'isotope': ['Isotope not registered.']}


def test_invalid_missing_field(lu_177):

    form = IsotopeForm({})

    assert not form.is_valid()

    assert form.errors == {'isotope': ['This field is required.']}
