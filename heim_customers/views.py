from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR

from heim_customers.models import Customer
from heim_customers.serializers import ReadCustomerSerializer
from heim_utils.utils import generic_api_response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_customers(request):
    try:
        customers = Customer.objects.all()
        serializer = ReadCustomerSerializer(customers, many=True)
        return generic_api_response(200, serializer.data)
    except Exception as e:
        return generic_api_response(HTTP_500_INTERNAL_SERVER_ERROR, None, e)
