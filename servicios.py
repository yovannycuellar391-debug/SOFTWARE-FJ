from abc import ABC, abstractmethod
from entidades import EntidadBase
from excepciones import ErrorCalculoCosto, ErrorValidacionDato


class Servicio(EntidadBase, ABC):
    def __init__(self, id_entidad: str, nombre: str, tarifa_base: float, disponible: bool = True) -> None:
        super().__init__(id_entidad)
        if not isinstance(nombre, str) or not nombre.strip():
            raise ErrorValidacionDato("El nombre del servicio es obligatorio.")
        if not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            raise ErrorValidacionDato("La tarifa base debe ser un número mayor que cero.")

        self.nombre = nombre.strip()
        self.tarifa_base = float(tarifa_base)
        self.disponible = bool(disponible)

    @abstractmethod
    def validar_parametros(self, cantidad_o_horas: float, **kwargs) -> None:
        pass

    @abstractmethod
    def describir(self) -> str:
        pass

    def calcular_costo(
        self,
        cantidad_o_horas: float,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
        recargo_extra: float = 0.0,
        **kwargs,
    ) -> float:
        """
        Variantes de cálculo:
        - Solo tarifa_base * cantidad_o_horas
        - Con descuento_pct y/o impuesto_pct
        - Con recargo_extra u otros parámetros opcionales (**kwargs)
        """
        try:
            if isinstance(cantidad_o_horas, bool) or not isinstance(cantidad_o_horas, (int, float)):
                raise ErrorCalculoCosto("La duración o cantidad debe ser numérica.")
            if cantidad_o_horas <= 0:
                raise ErrorCalculoCosto("La duración o cantidad debe ser mayor que cero.")
            if not (0 <= descuento_pct < 100):
                raise ErrorCalculoCosto("El descuento debe estar entre 0 y menos de 100%.")
            if impuesto_pct < 0 or recargo_extra < 0:
                raise ErrorCalculoCosto("Impuestos y recargos no pueden ser negativos.")

            self.validar_parametros(cantidad_o_horas, **kwargs)

            subtotal = self.tarifa_base * float(cantidad_o_horas) + float(recargo_extra)
            con_descuento = subtotal * (1 - float(descuento_pct) / 100.0)
            total = con_descuento * (1 + float(impuesto_pct) / 100.0)

            if total <= 0:
                raise ErrorCalculoCosto("El total calculado no es válido.")
            return round(total, 2)
        except ErrorCalculoCosto:
            raise
        except Exception as exc:
            raise ErrorCalculoCosto(f"Error al calcular costo en '{self.nombre}'.") from exc

    def resumen(self) -> str:
        estado = "Disponible" if self.disponible else "No disponible"
        return f"{self.describir()} | Tarifa: ${self.tarifa_base:,.2f} | {estado}"


class ReservaSala(Servicio):
    def __init__(self, id_entidad: str, nombre: str, tarifa_base: float, capacidad: int, disponible: bool = True) -> None:
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ErrorValidacionDato("La capacidad de la sala debe ser un entero positivo.")
        self.capacidad = capacidad
        super().__init__(id_entidad, nombre, tarifa_base, disponible)
        self.validar()

    def validar(self) -> None:
        if self.capacidad <= 0:
            raise ErrorValidacionDato("Capacidad inválida.")

    def validar_parametros(self, cantidad_o_horas: float, asistentes: int = 1, **kwargs) -> None:
        if not isinstance(asistentes, int) or asistentes <= 0:
            raise ErrorValidacionDato("El número de asistentes debe ser entero y mayor que cero.")
        if asistentes > self.capacidad:
            raise ErrorValidacionDato(
                f"La sala '{self.nombre}' admite máximo {self.capacidad} personas (solicitados: {asistentes})."
            )

    def describir(self) -> str:
        return f"Sala [{self.id}] {self.nombre} (Cap. {self.capacidad} pers.)"


class AlquilerEquipo(Servicio):
    def __init__(self, id_entidad: str, nombre: str, tarifa_base: float, stock_unidades: int, disponible: bool = True) -> None:
        if not isinstance(stock_unidades, int) or stock_unidades < 0:
            raise ErrorValidacionDato("El stock de equipos no puede ser negativo.")
        self.stock_unidades = stock_unidades
        super().__init__(id_entidad, nombre, tarifa_base, disponible and stock_unidades > 0)
        self.validar()

    def validar(self) -> None:
        if self.stock_unidades < 0:
            raise ErrorValidacionDato("Stock inválido.")

    def validar_parametros(self, cantidad_o_horas: float, unidades: int = 1, **kwargs) -> None:
        if not isinstance(unidades, int) or unidades <= 0:
            raise ErrorValidacionDato("Las unidades a alquilar deben ser un entero positivo.")
        if unidades > self.stock_unidades:
            raise ErrorValidacionDato(
                f"Solo hay {self.stock_unidades} unidades de '{self.nombre}' (solicitadas: {unidades})."
            )

    def describir(self) -> str:
        return f"Equipo [{self.id}] {self.nombre} (Stock: {self.stock_unidades})"


class AsesoriaEspecializada(Servicio):
    def __init__(self, id_entidad: str, nombre: str, tarifa_base: float, especialidad: str, disponible: bool = True) -> None:
        if not isinstance(especialidad, str) or not especialidad.strip():
            raise ErrorValidacionDato("La especialidad de la asesoría es obligatoria.")
        self.especialidad = especialidad.strip()
        super().__init__(id_entidad, nombre, tarifa_base, disponible)
        self.validar()

    def validar(self) -> None:
        if not self.especialidad:
            raise ErrorValidacionDato("Especialidad vacía.")

    def validar_parametros(self, cantidad_o_horas: float, **kwargs) -> None:
        if cantidad_o_horas > 12:
            raise ErrorValidacionDato("Una sesión de asesoría no puede exceder 12 horas seguidas.")

    def describir(self) -> str:
        return f"Asesoría [{self.id}] {self.nombre} ({self.especialidad})"