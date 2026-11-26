from entidades import Cliente, EntidadBase
from excepciones import ErrorDisponibilidadReserva, ErrorOperacionNoPermitida, ErrorValidacionDato
from servicios import Servicio


class Reserva(EntidadBase):
    ESTADOS_VALIDOS = ("pendiente", "confirmada", "cancelada")

    def __init__(
        self,
        id_entidad: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion_o_cantidad: float,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
        **detalle_servicio,
    ) -> None:
        super().__init__(id_entidad)
        if not isinstance(cliente, Cliente):
            raise ErrorValidacionDato("Se requiere una instancia válida de Cliente.")
        if not isinstance(servicio, Servicio):
            raise ErrorValidacionDato("Se requiere una instancia válida de Servicio.")
        if not servicio.disponible:
            raise ErrorDisponibilidadReserva(f"El servicio '{servicio.nombre}' no está disponible.")

        servicio.validar_parametros(duracion_o_cantidad, **detalle_servicio)
        costo_estimado = servicio.calcular_costo(
            duracion_o_cantidad,
            descuento_pct=descuento_pct,
            impuesto_pct=impuesto_pct,
        )

        self.cliente = cliente
        self.servicio = servicio
        self.duracion_o_cantidad = float(duracion_o_cantidad)
        self.detalle_servicio = detalle_servicio
        self.total = costo_estimado
        self.estado = "pendiente"
        self.validar()

    def validar(self) -> None:
        if self.estado not in self.ESTADOS_VALIDOS:
            raise ErrorOperacionNoPermitida(f"Estado de reserva no válido: '{self.estado}'.")
        if self.duracion_o_cantidad <= 0:
            raise ErrorValidacionDato("La duración o cantidad debe ser mayor que cero.")

    def confirmar(self) -> None:
        if self.estado == "cancelada":
            raise ErrorOperacionNoPermitida(f"No se puede confirmar la reserva '{self.id}' porque está cancelada.")
        if self.estado == "confirmada":
            raise ErrorOperacionNoPermitida(f"La reserva '{self.id}' ya se encuentra confirmada.")
        if not self.servicio.disponible:
            raise ErrorDisponibilidadReserva(f"El servicio '{self.servicio.nombre}' dejó de estar disponible.")
        self.estado = "confirmada"

    def cancelar(self) -> None:
        if self.estado == "cancelada":
            raise ErrorOperacionNoPermitida(f"La reserva '{self.id}' ya está cancelada.")
        self.estado = "cancelada"

    def procesar(self, confirmar_automaticamente: bool = True) -> float:
        self.validar()
        if confirmar_automaticamente and self.estado == "pendiente":
            self.confirmar()
        return self.total

    def resumen(self) -> str:
        return (
            f"Reserva [{self.id}] | Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | Total: ${self.total:,.2f} | Estado: {self.estado}"
        )