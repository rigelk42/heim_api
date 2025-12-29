from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from customer_management.application import (CreateCustomerCommand,
                                             CustomerCommandHandler,
                                             CustomerQueryHandler,
                                             DeleteCustomerCommand,
                                             GetCustomerQuery,
                                             ListCustomersQuery,
                                             SearchCustomersQuery,
                                             UpdateCustomerCommand)
from customer_management.domain.exceptions import (CustomerAlreadyExists,
                                                   CustomerNotFound)


class CustomerListCreateView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command_handler = CustomerCommandHandler()
        self.query_handler = CustomerQueryHandler()

    def get(self, request):
        search = request.query_params.get("q")

        if search:
            query = SearchCustomersQuery(query=search)
            customers = self.query_handler.handle_search(query)
        else:
            query = ListCustomersQuery()
            customers = self.query_handler.handle_list(query)

        data = [
            {
                "id": c.id,
                "given_names": c.given_names,
                "surnames": c.surnames,
                "full_name": c.full_name,
                "email": c.email,
                "phone": c.phone,
            }
            for c in customers
        ]
        return Response(data)

    def post(self, request):
        command = CreateCustomerCommand(
            given_names=request.data.get("given_names", ""),
            surnames=request.data.get("surnames", ""),
            email=request.data.get("email", ""),
            phone=request.data.get("phone", ""),
        )

        try:
            customer = self.command_handler.handle_create(command)
        except CustomerAlreadyExists as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "id": customer.id,
                "given_names": customer.given_names,
                "surnames": customer.surnames,
                "full_name": customer.full_name,
                "email": customer.email,
                "phone": customer.phone,
            },
            status=status.HTTP_201_CREATED,
        )


class CustomerDetailView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command_handler = CustomerCommandHandler()
        self.query_handler = CustomerQueryHandler()

    def get(self, request, customer_id: int):
        query = GetCustomerQuery(customer_id=customer_id)

        try:
            customer = self.query_handler.handle_get(query)
        except CustomerNotFound:
            return Response(
                {"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                "id": customer.id,
                "given_names": customer.given_names,
                "surnames": customer.surnames,
                "full_name": customer.full_name,
                "email": customer.email,
                "phone": customer.phone,
            }
        )

    def patch(self, request, customer_id: int):
        command = UpdateCustomerCommand(
            customer_id=customer_id,
            given_names=request.data.get("given_names"),
            surnames=request.data.get("surnames"),
            phone=request.data.get("phone"),
        )

        try:
            customer = self.command_handler.handle_update(command)
        except CustomerNotFound:
            return Response(
                {"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "id": customer.id,
                "given_names": customer.given_names,
                "surnames": customer.surnames,
                "full_name": customer.full_name,
                "email": customer.email,
                "phone": customer.phone,
            }
        )

    def delete(self, request, customer_id: int):
        command = DeleteCustomerCommand(customer_id=customer_id)

        try:
            self.command_handler.handle_delete(command)
        except CustomerNotFound:
            return Response(
                {"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
