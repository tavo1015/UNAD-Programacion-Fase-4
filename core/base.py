# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programacion (Codigo: 213023)
# Fase 4 - Practicas Simuladas (Software FJ)
# Modulo: Arquitectura Base

from abc import ABC, abstractmethod
from datetime import datetime


class EntidadBase(ABC):
    """
    Clase abstracta base para las entidades del sistema Software FJ.
    """

    def __init__(self, id_entidad: str):
        # Identificador unico de la entidad
        self._id_entidad = str(id_entidad).strip()
        # Fecha y hora de creacion en memoria
        self._fecha_registro = datetime.now()

    @property
    def id_entidad(self) -> str:
        """Retorna el identificador unico de la entidad."""
        return self._id_entidad

    @property
    def fecha_registro(self) -> datetime:
        """Retorna la fecha de registro del objeto."""
        return self._fecha_registro

    @abstractmethod
    def obtener_detalle(self) -> dict:
        """Contrato abstracto que implementaran las clases hijas."""
        pass
