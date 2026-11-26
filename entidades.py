from abc import ABC, abstractmethod
import re
from excepciones import ErrorValidacionDato


class EntidadBase(ABC):
    def __init__(self, id_entidad: str) -> None:
        if not isinstance(id_entidad, str) or not id_entidad.strip():
            raise ErrorValidacionDato("El ID de la entidad no puede estar vacío.")
        self._id = id_entidad.strip()

    @property
    def id(self) -> str:
        return self._id

    @abstractmethod
    def validar(self) -> None:
        pass

    @abstractmethod
    def resumen(self) -> str:
        pass


class Cliente(EntidadBase):
    def __init__(self, id_entidad: str, nombre: str, correo: str, telefono: str) -> None:
        super().__init__(id_entidad)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        self.validar()

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or len(valor.strip()) < 2:
            raise ErrorValidacionDato("El nombre del cliente debe tener al menos 2 caracteres.")
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        if not isinstance(valor, str) or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", valor.strip()):
            raise ErrorValidacionDato(f"Correo electrónico inválido: '{valor}'.")
        self._correo = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        limpio = valor.strip() if isinstance(valor, str) else ""
        if len(limpio) < 7 or not limpio.isdigit():
            raise ErrorValidacionDato("El teléfono debe contener solo dígitos (mínimo 7).")
        self._telefono = limpio

    def validar(self) -> None:
        if not self._nombre or not self._correo or not self._telefono:
            raise ErrorValidacionDato("Datos incompletos en el cliente.")

    def resumen(self) -> str:
        return f"Cliente [{self.id}] {self.nombre} | {self.correo} | Tel: {self.telefono}"