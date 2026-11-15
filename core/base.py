# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programacion (Codigo: 213023)
# Fase 4 - Practicas Simuladas (Software FJ)
# Modulo: Arquitectura Base

from abc import ABC, abstractmethod
from datetime import datetime


class EntidadBase(ABC):
    """
    Clase abstracta base para todas las entidades del sistema Software FJ.
    Incluye control de estado activo/inactivo y validacion de tipos.
    """

    def __init__(self, id_entidad: str):
        self._id_entidad = str(id_entidad).strip()
        self._fecha_registro = datetime.now()
        self._activo = True

    @property
    def id_entidad(self) -> str:
        """Retorna el identificador unico de la entidad."""
        return self._id_entidad

    @property
    def fecha_registro(self) -> datetime:
        """Retorna la fecha y hora exacta en la que se creo la entidad."""
        return self._fecha_registro

    @property
    def activo(self) -> bool:
        """Indica si el elemento esta activo en el sistema."""
        return self._activo

    @activo.setter
    def activo(self, nuevo_estado: bool):
        """Valida y actualiza el estado de actividad de la entidad."""
        if not isinstance(nuevo_estado, bool):
            raise TypeError("El estado activo debe ser un valor booleano (True o False).")
        self._activo = nuevo_estado

    @abstractmethod
    def obtener_detalle(self) -> dict:
        """Contrato abstracto para obtener los datos estructurados del objeto."""
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id='{self._id_entidad}' activo={self._activo}>"
