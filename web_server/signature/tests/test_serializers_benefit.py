from web_server.signature.serializers import BenefitSerializer


def test_benefit_serializer(benefit):

    serializer = BenefitSerializer(instance=benefit)

    data = serializer.data

    assert data['uuid'] == str(benefit.uuid)
    assert data['name'] == 'RSV'
    assert data['uri'] == '/dashboard/my-signatures/Benefit/calculator'
