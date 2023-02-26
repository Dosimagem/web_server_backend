import pytest

from web_server.conftest import fake


@pytest.fixture
def contact_data():
    return {
        'full_name': fake.name(),
        'email': fake.email(),
        'role': fake.company()[:30],
        'clinic': fake.job()[:30],
        'phone': '+552123612766',
        'subject': fake.sentence(4),
        'message': fake.sentence(10),
    }


@pytest.fixture
def contact_payload(contact_data):

    dict_ = contact_data.copy()

    dict_['fullName'] = dict_.pop('full_name')

    return dict_
