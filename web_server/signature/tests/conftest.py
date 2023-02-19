import pytest

from web_server.signature.models import Benefit, Signature


@pytest.fixture
def benefit(db):
    return Benefit.objects.create(name='RSV', uri='/dashboard/my-signatures/Benefit/calculator')


@pytest.fixture
def benefit_list(db):
    b1 = Benefit(name='B1', uri='/Benefit/B1')
    b2 = Benefit(name='B2', uri='/Benefit/B2')
    b3 = Benefit(name='B3', uri='/Benefit/B3')
    return Benefit.objects.bulk_create([b1, b2, b3])


@pytest.fixture
def user_signature(user, benefit_list):

    sig = Signature.objects.create(user=user, plan='Pacote Dosimagem mensal', price='60.00')

    sig.benefits.add(*benefit_list)

    return sig


@pytest.fixture
def user_other_signature(user, benefit_list):

    sig = Signature.objects.create(user=user, plan='Pacote Dosimagem Anual', price='600.00')

    sig.benefits.add(benefit_list[0])

    return sig


@pytest.fixture
def signature_payload(benefit_list):
    return {
        'plan': 'Custom RSV',
        'modality': 'monthly',
        'trialTime': '30 days',
        'price': '60.00',
        'discount': '10.00',
        'benefits': [
            'B1',
            'B2',
            'B3',
        ],
    }
