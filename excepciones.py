class ErrorSoftwareFJ(Exception):
    """Excepción base para todos los errores de Software FJ."""


class ErrorValidacionDato(ErrorSoftwareFJ):
    """Datos inválidos, vacíos o fuera de rango."""


class ErrorOperacionNoPermitida(ErrorSoftwareFJ):
    """Transiciones de estado o acciones no válidas."""


class ErrorDisponibilidadReserva(ErrorSoftwareFJ):
    """Problemas de disponibilidad, cupo o creación/procesamiento de reservas."""


class ErrorCalculoCosto(ErrorSoftwareFJ):
    """Errores al calcular tarifas, descuentos, impuestos o totales."""