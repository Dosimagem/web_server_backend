from web_server.isotope.forms import IsotopeDosimetryForm, IsotopeRadiosynoForm


class TestIsotopeDosimetryForm:
    def test_valid(self, lu_177):

        form = IsotopeDosimetryForm({'isotope': 'Lu-177'})
        assert form.is_valid()

    def test_invalid_by_not_registered(self, lu_177):

        form = IsotopeDosimetryForm({'isotope': 'Lu-17'})

        assert not form.is_valid()

        assert form.errors == {'isotope': ['Isótopo não registrado.']}

    def test_invalid_missing_field(self, lu_177):

        form = IsotopeDosimetryForm({})

        assert not form.is_valid()

        assert form.errors == {'isotope': ['Este campo é obrigatório.']}


class TestIsotopeRadiosynoForm:
    def test_valid(self, y_90):

        form = IsotopeRadiosynoForm({'isotope': 'Y-90'})

        assert form.is_valid()

    def test_invalid_by_not_registered(self, y_90):

        form = IsotopeRadiosynoForm({'isotope': 'Lu-17'})

        assert not form.is_valid()

        assert form.errors == {'isotope': ['Isótopo não registrado.']}

    def test_invalid_missing_field(self, y_90):

        form = IsotopeRadiosynoForm({})

        assert not form.is_valid()

        assert form.errors == {'isotope': ['Este campo é obrigatório.']}
