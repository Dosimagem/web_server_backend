from datetime import datetime
from decimal import Decimal
from http import HTTPStatus
from uuid import uuid4

from attrs import asdict, define, field
from rest_framework.decorators import api_view
from rest_framework.response import Response

from web_server.core.decorators import user_from_token_and_user_from_url
from web_server.signature.models import Signature
from web_server.signature.serializers import SignatureByUserSerializer


@define
class Benefit:
    id = field(converter=str)
    name: str = field()
    uri: str = field()


Benefit1 = Benefit(id=uuid4(), name='RSV', uri='/dashboard/my-signatures/Benefit/calculator')
Benefit2 = Benefit(id=uuid4(), name='Beneficio B', uri='/dashboard/my-signatures/Benefit/beneficiob')
Benefit3 = Benefit(id=uuid4(), name='Beneficio C', uri='/dashboard/my-signatures/Benefit/beneficioc')


@define
class Signatures:
    id = field(converter=str)
    name: str = field()
    Benefit: list = field()
    price: Decimal = field()
    hired_period: dict = field()
    test_period: dict = field()
    activated: bool = field()
    bill_file: str = field()


signature1 = Signatures(
    'e3b6a8d7-3bb3-4d2e-9f44-5c1780c214cf',
    'Pacote Dosimagem mensal',
    [
        asdict(Benefit1),
        asdict(Benefit2),
        asdict(Benefit3),
    ],
    Decimal('60.00'),
    None,
    {
        'initial': datetime(2022, 10, 11).strftime('%Y-%m-%d'),
        'end': datetime(2022, 11, 11).strftime('%Y-%m-%d'),
    },
    True,
    bill_file='',
)

signature2 = Signatures(
    '9e00ee87-2223-4807-9885-11161b88bac1',
    'Pacote Dosimagem Anual',
    [
        asdict(Benefit1),
        asdict(Benefit2),
        asdict(Benefit3),
    ],
    Decimal('600.00'),
    {
        'initial': datetime(2022, 10, 11).strftime('%Y-%m-%d'),
        'end': datetime(2023, 10, 11).strftime('%Y-%m-%d'),
    },
    None,
    True,
    bill_file='',
)

LIST_SIGNATURES = [signature1, signature2]
# LIST_SIGNATURES = [signature1]


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
@user_from_token_and_user_from_url
def signature_list(request, user_id):

    user = request.user

    qs = user.signatures.all()

    serializer = SignatureByUserSerializer(qs, many=True)

    list_ = serializer.data

    return Response(data={'count': len(list_), 'row': list_})


@api_view(['GET'])
@user_from_token_and_user_from_url
def signature_read(request, user_id, signature_id):

    user = request.user

    try:
        signature = user.signatures.get(uuid=signature_id)
    except Signature.DoesNotExist:
        return Response(data={'errors': 'Assinatura não encontrada para esse usuário'}, status=HTTPStatus.NOT_FOUND)

    serializer = SignatureByUserSerializer(signature)

    return Response(data=serializer.data)
