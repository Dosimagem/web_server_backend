from uuid import uuid4
from datetime import datetime
from decimal import Decimal

from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)
from rest_framework.permissions import IsAuthenticated
from web_server.api.decorators import user_from_token_and_user_from_url
from web_server.api.views.auth import MyTokenAuthentication

LIST_BENEFITS = [
    {
        "id": uuid4(),
        "name": "RSV",
        "hired_period": {
            "initial": datetime(2022, 10, 11).strftime('%Y-%m-%d'),
            "end": datetime(2022, 11, 11).strftime('%Y-%m-%d'),
        },
        "test_period": None,
        "price": Decimal('1000.00'),
        "activated": True
    },
    {
        "id": uuid4(),
        "name": "Benificio1",
        "hired_period": None,
        "test_period": {
            "initial": datetime(2022, 6, 11).strftime('%Y-%m-%d'),
            "end": datetime(2022, 7, 11).strftime('%Y-%m-%d'),
        },
        "price": Decimal('3400.00'),
        "activated": True
    },
    {
        "id": uuid4(),
        "name": "Benificio2",
        "hired_period": None,
        "test_period": None,
        "price": Decimal('3400.00'),
        "activated": False
    }
]


class Benefits():

    def __init__(self, list_):
        self._list = list_

    def find(self, id):
        for benefit in self._list:
            if id == benefit['id']:
                return benefit
        return None

    def all(self):
        return self._list


benefits_fake_db = Benefits(LIST_BENEFITS)


@api_view(['GET'])
@authentication_classes([MyTokenAuthentication])
@permission_classes([IsAuthenticated])
@user_from_token_and_user_from_url
def benefit_list(request, user_id):

    benefit_list = benefits_fake_db.all()

    data = {
        'count': len(benefit_list),
        'row': benefit_list
    }

    return Response(data=data)


@api_view(['GET'])
@authentication_classes([MyTokenAuthentication])
@permission_classes([IsAuthenticated])
@user_from_token_and_user_from_url
def benefit_read(request, user_id, benefit_id):

    benefit = benefits_fake_db.find(benefit_id)

    return Response(data=benefit)