class CustomerException(Exception):
    pass


class CustomerNotFound(CustomerException):
    def __init__(self, identifier: int | str):
        self.identifier = identifier
        super().__init__(f"Customer not found: {identifier}")


class CustomerAlreadyExists(CustomerException):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Customer with email {email} already exists")
