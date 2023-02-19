from datetime import date

from freezegun import freeze_time

from web_server.signature.service_layer import new_test_period


@freeze_time('2022-02-01 00:00:00')
def test_period_test():

    range = new_test_period()

    expected = {
        'test_period_initial': date.fromisoformat('2022-02-01'),
        'test_period_end': date.fromisoformat('2022-03-03'),
    }

    assert range == expected
