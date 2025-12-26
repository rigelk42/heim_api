from django.db.models import Q, QuerySet

from customers.domain.models import Customer


class CustomerRepository:
    def get_all(self) -> QuerySet[Customer]:
        return Customer.objects.all()

    def get_by_id(self, customer_id: int) -> Customer | None:
        return Customer.objects.filter(id=customer_id).first()

    def get_by_email(self, email: str) -> Customer | None:
        return Customer.objects.filter(email=email).first()

    def search(self, query: str) -> QuerySet[Customer]:
        return Customer.objects.filter(
            Q(given_names__icontains=query)
            | Q(surnames__icontains=query)
            | Q(email__icontains=query)
        )

    def save(self, customer: Customer) -> Customer:
        customer.full_clean()
        customer.save()
        return customer

    def create(
        self,
        given_names: str,
        surnames: str,
        email: str,
        phone: str = "",
    ) -> Customer:
        customer = Customer(
            given_names=given_names,
            surnames=surnames,
            email=email,
            phone=phone,
        )
        customer.full_clean()
        customer.save()
        return customer

    def delete(self, customer: Customer) -> None:
        customer.delete()
