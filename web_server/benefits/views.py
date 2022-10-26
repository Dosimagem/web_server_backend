from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from attrs import asdict, define, field
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from web_server.core.decorators import user_from_token_and_user_from_url
from web_server.core.views.auth import MyTokenAuthentication


@define
class Benefits:
    id = field(converter=str)
    name: str = field()
    uri: str = field()


benefit1 = Benefits(id=uuid4(), name='RSV', uri='/dashboard/my-signatures/benefits/calculator')
benefit2 = Benefits(id=uuid4(), name='Beneficio B', uri='/dashboard/my-signatures/benefits/beneficiob')
benefit3 = Benefits(id=uuid4(), name='Beneficio C', uri='/dashboard/my-signatures/benefits/beneficioc')


@define
class Signatures:
    id = field(converter=str)
    name: str = field()
    benefits: list = field()
    price: Decimal = field()
    hired_period: dict = field()
    test_period: dict = field()
    activated: bool = field()


signature1 = Signatures(
    'e3b6a8d7-3bb3-4d2e-9f44-5c1780c214cf',
    'Assinatura 1',
    [
        asdict(benefit1),
        asdict(benefit2),
    ],
    Decimal('1000.00'),
    {
        'initial': datetime(2022, 10, 11).strftime('%Y-%m-%d'),
        'end': datetime(2022, 11, 11).strftime('%Y-%m-%d'),
    },
    None,
    True,
)

signature2 = Signatures(
    '9e00ee87-2223-4807-9885-11161b88bac1',
    'Assinatura 2',
    [
        asdict(benefit1),
        asdict(benefit3),
    ],
    Decimal('4000.00'),
    None,
    {
        'initial': datetime(2022, 10, 11).strftime('%Y-%m-%d'),
        'end': datetime(2022, 11, 11).strftime('%Y-%m-%d'),
    },
    True,
)

signature3 = Signatures(
    '89a88a2c-b2ee-49d8-b2c0-5f4373b5446f',
    'Assinatura 3',
    [
        asdict(benefit1),
        asdict(benefit3),
    ],
    Decimal('2000.00'),
    None,
    None,
    False,
)


LIST_SIGNATURES = [signature1, signature2, signature3]


class SignatureModel:
    def __init__(self, list_):
        self._list = list_

    def find(self, id):
        for signature in self._list:
            if str(id) == signature.id:
                return signature
        return None

    def all(self):
        return self._list


signatures_fake_db = SignatureModel(LIST_SIGNATURES)


@api_view(['GET'])
@authentication_classes([MyTokenAuthentication])
@permission_classes([IsAuthenticated])
@user_from_token_and_user_from_url
def signature_list(request, user_id):

    signature_list = [asdict(s) for s in signatures_fake_db.all()]

    data = {'count': len(signature_list), 'row': signature_list}

    return Response(data=data)


@api_view(['GET'])
@authentication_classes([MyTokenAuthentication])
@permission_classes([IsAuthenticated])
@user_from_token_and_user_from_url
def signature_read(request, user_id, signature_id):

    signature = signatures_fake_db.find(signature_id)

    return Response(data=asdict(signature))
