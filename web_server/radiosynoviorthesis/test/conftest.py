import pytest


@pytest.fixture
def calculator_input():
    return {
        'radionuclide': 'Lu-177',
        'thickness': '1 mm',
        'surface': 10
    }
