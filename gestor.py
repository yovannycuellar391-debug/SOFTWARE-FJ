import logging
from pathlib import Path
from entidades import Cliente
from excepciones import ErrorCalculoCosto, ErrorOperacionNoPermitida, ErrorValidacionDato
from reservas import Reserva
from servicios import Servicio


def configurar_logger(ruta_log: str = "logs/software_fj.log") -> logging.Logger:
    archivo = Path(ruta_log)
    archivo.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formato = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(archivo, encoding="utf-8")
    file_handler.setFormatter(formato)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formato)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


class SistemaGestionFJ:
    def __init__(self, ruta_log: str = "logs/software_fj.log") -> None:
        self.clientes: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []
        self.logger = configurar_logger(ruta_log)

    def registrar_cliente(self, cliente: Cliente) -> None:
        if any(c.id == cliente.id for c in self.clientes):
            raise ErrorValidacionDato(f"Ya existe un cliente con ID '{cliente.id}'.")
        self.clientes.append(cliente)
        self.logger.info(f"Cliente registrado: {cliente.resumen()}")

    def registrar_servicio(self, servicio: Servicio) -> None:
        if any(s.id == servicio.id for s in self.servicios):
            raise ErrorValidacionDato(f"Ya existe un servicio con ID '{servicio.id}'.")
        self.servicios.append(servicio)
        self.logger.info(f"Servicio registrado: {servicio.resumen()}")

    def buscar_cliente(self, id_cliente: str) -> Cliente:
        for c in self.clientes:
            if c.id == id_cliente:
                return c
        raise ErrorValidacionDato(f"Cliente con ID '{id_cliente}' no encontrado.")

    def buscar_servicio(self, id_servicio: str) -> Servicio:
        for s in self.servicios:
            if s.id == id_servicio:
                return s
        raise ErrorValidacionDato(f"Servicio con ID '{id_servicio}' no encontrado.")

    def crear_reserva(
        self,
        id_reserva: str,
        id_cliente: str,
        id_servicio: str,
        duracion_o_cantidad: float,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
        confirmar_inmediato: bool = True,
        **detalle_servicio,
    ) -> Reserva:
        if any(r.id == id_reserva for r in self.reservas):
            raise ErrorOperacionNoPermitida(f"Ya existe una reserva con ID '{id_reserva}'.")

        cliente = self.buscar_cliente(id_cliente)
        servicio = self.buscar_servicio(id_servicio)
        reserva = Reserva(
            id_entidad=id_reserva,
            cliente=cliente,
            servicio=servicio,
            duracion_o_cantidad=duracion_o_cantidad,
            descuento_pct=descuento_pct,
            impuesto_pct=impuesto_pct,
            **detalle_servicio,
        )
        reserva.procesar(confirmar_automaticamente=confirmar_inmediato)
        self.reservas.append(reserva)
        self.logger.info(f"Reserva creada: {reserva.resumen()}")
        return reserva

    def cancelar_reserva(self, id_reserva: str) -> None:
        for r in self.reservas:
            if r.id == id_reserva:
                r.cancelar()
                self.logger.info(f"Reserva cancelada: {r.resumen()}")
                return
        raise ErrorOperacionNoPermitida(f"No se encontró la reserva '{id_reserva}' para cancelar.")

    def calcular_con_encadenamiento(self, id_servicio: str, horas: float, divisor_prorrateo: float) -> float:
        servicio = self.buscar_servicio(id_servicio)
        try:
            total = servicio.calcular_costo(horas)
            return round(total / divisor_prorrateo, 2)
        except ZeroDivisionError as exc:
            raise ErrorCalculoCosto("No se puede prorratear un costo entre cero.") from exc
        except TypeError as exc:
            raise ErrorCalculoCosto("Tipos incompatibles en el cálculo del costo.") from exc