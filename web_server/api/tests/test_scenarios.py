# import pytest
# from decimal import Decimal

# from rest_framework.authtoken.models import Token

# from web_server.service.models import UserQuota
# from web_server.core.models import UserProfile
# from web_server.core.models import CustomUser as User



# @pytest.fixture
# def case1(user_profile_info):

#     user1_infos = {
#         'email': 'test1@test.com',
#         'password': '123456!!'
#     }

#     user2_info = {
#         'email': 'test2@test.com',
#         'password': '123456##'
#     }

#     user1 = User.objects.create_user(**user1_infos)
#     UserProfile.objects.update(**user_profile_info)
#     Token.objects.create(user=user1)

#     user2 = User.objects.create_user(**user2_info)
#     UserProfile.objects.update(**user_profile_info)
#     Token.objects.create(user=user2)

#     user1_q1 = UserQuota(user=user1,
#                    type=UserQuota.DOSIMETRY_CLINIC,
#                    number=10,
#                    value=Decimal('10000.00'),
#                    status_payment=UserQuotas.CONFIRMED)

#     user1_q2 = UserQuota(user=user1,
#                    type=UserQuota.DOSIMETRY_PRECLINIC,
#                    number=10,
#                    value=Decimal('10000.00'),
#                    status_payment=UserQuotas.ANALYSIS)

#     user2_q2 = UserQuota(user=user1,
#                    type=UserQuota.DOSIMETRY_CLINIC,
#                    number=3,
#                    value=Decimal('1000.00'),
#                    status_payment=UserQuotas.COMFIRMED)


#     UserQuota.objects.bulk_create([user1_q1, user1_q2, user2_q2])




# def test_scenario_case1():
#     '''

#     UserQuota Table:

#     ID_USER  Type               Number    Value   Status Payment
#     1        Dosimetry Clinic     10     10.000   Confirmed
#     1        Dosimetry Preclinic   5      5.000   Analysis
#     2        Dosimetry Clinic      3      3.000   Confimed


#     DosimetryClinic Table:

#     ID_USER ID_QUOTAS Infos
#     1       1         Info1
#     1       1         Indo2
#     2       3         Info1
#     1       1         Info3

#     DosimetryPreclinic Table

#     ID_USER ID_QUOTAS Infos
#     1       2          Infos1
#     1       2          Infos2

#     '''
