import pytest

from web_server.conftest import fake


@pytest.fixture
def contact_data():
    return {
        'name': fake.name(),
        'email': fake.email(),
        'role': fake.company()[:30],
        'company': fake.job()[:30],
        'number': '+552123612766',
        'subject': fake.sentence(4),
        'message': fake.sentence(10),
    }


@pytest.fixture
def contact_payload(contact_data):
    return contact_data.copy()
