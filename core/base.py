# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programacion (Codigo: 213023)
# Fase 4 - Practicas Simuladas (Software FJ)
# Modulo: Arquitectura Base
# Descripcion: Define la clase abstracta fundamental de la cual heredan todas
# las entidades del sistema (Clientes, Servicios y Reservas).

from abc import ABC, abstractmethod
from datetime import datetime


class EntidadBase(ABC):
    """
    Clase abstracta base para todas las entidades del sistema Software FJ.
    Aplica el principio de abstraccion de la Programacion Orientada a Objetos,
    definiendo atributos comunes y forzando a las clases hijas a implementar
    metodos esenciales como obtener_detalle().
    """

    def __init__(self, id_entidad: str):
        # Identificador unico de la entidad (ej: cedula, codigo de servicio, id reserva)
        self._id_entidad = str(id_entidad).strip()
        # Marca de tiempo de registro automatico en el sistema
        self._fecha_registro = datetime.now()
        # Estado activo de la entidad en memoria
        self._activo = True

    # Getter para el identificador unico
    @property
    def id_entidad(self) -> str:
        """Retorna el identificador unico de la entidad."""
        return self._id_entidad

    # Getter para la fecha de creacion
    @property
    def fecha_registro(self) -> datetime:
        """Retorna la fecha y hora exacta en la que se creo la entidad."""
        return self._fecha_registro

    # Getter para el estado de actividad
    @property
    def activo(self) -> bool:
        """Indica si el elemento esta activo en el sistema."""
        return self._activo

    # Setter para modificar el estado de actividad con validacion booleana
    @activo.setter
    def activo(self, nuevo_estado: bool):
        """Permite habilitar o deshabilitar la entidad."""
        if not isinstance(nuevo_estado, bool):
            raise TypeError("El estado activo debe ser un valor booleano (True o False).")
        self._activo = nuevo_estado

    # Metodo abstracto obligatorio para todas las clases derivadas
    @abstractmethod
    def obtener_detalle(self) -> dict:
        """
        Metodo abstracto que debe ser sobrescrito por cualquier clase derivada
        para entregar un diccionario con los datos estructurados del objeto.
        """
        pass

    # Representacion generica en cadena de texto
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id='{self._id_entidad}' activo={self._activo}>"
