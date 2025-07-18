from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR

from heim_utils.utils import generic_api_response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_customer(request):
    try:
        pass
    except Exception as e:
        return generic_api_response(HTTP_500_INTERNAL_SERVER_ERROR, None, e)
