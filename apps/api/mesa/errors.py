class DomainError(Exception):
    """Error de negocio. `code` es estable para los clientes; el mensaje es legible."""

    code = "domain_error"

    def __init__(self, message: str = ""):
        super().__init__(message or self.code)
