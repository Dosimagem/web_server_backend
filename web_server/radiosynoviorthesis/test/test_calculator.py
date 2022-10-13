import pytest

from web_server.radiosynoviorthesis.calculator import radiosysnoviorthesis


@pytest.mark.parametrize(
    'thickness, surface, result',
    [
        ('1 mm', 10, {'MBq': 12.10, 'mCi': 0.33}),
        ('2 mm', 14, {'MBq': 22.08, 'mCi': 0.60}),
        ('3 mm', 3, {'MBq': 9.96, 'mCi': 0.27}),
    ],
)
def test_result_Y_90(thickness, surface, result):

    input = dict(radionuclide='Y-90', thickness=thickness, surface=surface)

    activity = radiosysnoviorthesis(**input)

    assert result == activity


@pytest.mark.parametrize(
    'thickness, surface, result',
    [
        ('1 mm', 10, {'MBq': 2.23, 'mCi': 0.06}),
        ('2 mm', 14, {'MBq': 4.39, 'mCi': 0.12}),
        ('3 mm', 3, {'MBq': 0.0, 'mCi': 0.0}),
    ],
)
def test_result_P_32(thickness, surface, result):

    input = dict(radionuclide='P-32', thickness=thickness, surface=surface)

    activity = radiosysnoviorthesis(**input)

    assert result == activity


@pytest.mark.parametrize(
    'thickness, surface, result',
    [
        ('1 mm', 10, {'MBq': 30.99, 'mCi': 0.84}),
        ('2 mm', 14, {'MBq': 65.61, 'mCi': 1.77}),
        ('3 mm', 3, {'MBq': 0.0, 'mCi': 0.0}),
    ],
)
def test_result_Re_188(thickness, surface, result):

    input = dict(radionuclide='Re-188', thickness=thickness, surface=surface)

    activity = radiosysnoviorthesis(**input)

    assert result == activity


@pytest.mark.parametrize(
    'thickness, surface, result',
    [
        ('1 mm', 10, {'MBq': 7.69, 'mCi': 0.21}),
        ('2 mm', 14, {'MBq': 0.0, 'mCi': 0.0}),
        ('3 mm', 3, {'MBq': 0.0, 'mCi': 0.0}),
    ],
)
def test_result_Re_186(thickness, surface, result):

    input = dict(radionuclide='Re-186', thickness=thickness, surface=surface)

    activity = radiosysnoviorthesis(**input)

    assert result == activity


@pytest.mark.parametrize(
    'thickness, surface, result',
    [
        ('1 mm', 10, {'MBq': 25.68, 'mCi': 0.69}),
        ('2 mm', 14, {'MBq': 0.0, 'mCi': 0.0}),
        ('3 mm', 3, {'MBq': 0.0, 'mCi': 0.0}),
    ],
)
def test_result_Sm_153(thickness, surface, result):

    input = dict(radionuclide='Sm-153', thickness=thickness, surface=surface)

    activity = radiosysnoviorthesis(**input)

    assert result == activity


@pytest.mark.parametrize(
    'thickness, surface, result',
    [
        ('1 mm', 10, {'MBq': 6.6, 'mCi': 0.18}),
        ('2 mm', 14, {'MBq': 0.0, 'mCi': 0.0}),
        ('3 mm', 3, {'MBq': 0.0, 'mCi': 0.0}),
    ],
)
def test_result_Lu_177(thickness, surface, result):

    input = dict(radionuclide='Lu-177', thickness=thickness, surface=surface)

    activity = radiosysnoviorthesis(**input)

    assert result == activity
