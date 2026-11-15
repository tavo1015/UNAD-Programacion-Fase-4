# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programacion (Codigo: 213023)
# Fase 4 - Practicas Simuladas (Software FJ)
# Modulo: Servicios Especializados
# Descripcion: Implementacion base de la clase abstracta Servicio y las
# subclases iniciales ReservaSala y AlquilerEquipo con validaciones basicas.

from abc import abstractmethod
from core.base import EntidadBase
from core.exceptions import ParametroInvalidoError


# =============================================================================
# CLASE ABSTRACTA: SERVICIO
# =============================================================================

class Servicio(EntidadBase):
    """
    Clase abstracta base para los servicios ofrecidos por Software FJ.
    Define el contrato minimo para los metodos polimorficos:
    calcular_costo(), describir_servicio() y validar_parametros().
    """

    def __init__(self, codigo_servicio: str, nombre: str, tarifa_base: float):
        super().__init__(id_entidad=codigo_servicio)

        if not nombre or len(str(nombre).strip()) < 3:
            raise ParametroInvalidoError("El nombre del servicio debe contener al menos 3 caracteres.")

        if tarifa_base <= 0:
            raise ParametroInvalidoError("La tarifa base del servicio debe ser mayor a cero.")

        self._codigo_servicio = str(codigo_servicio).strip()
        self._nombre = str(nombre).strip()
        self._tarifa_base = float(tarifa_base)

    @property
    def codigo_servicio(self) -> str:
        """Retorna el codigo unico del servicio."""
        return self._codigo_servicio

    @property
    def nombre(self) -> str:
        """Retorna el nombre comercial del servicio."""
        return self._nombre

    @property
    def tarifa_base(self) -> float:
        """Retorna el precio o tarifa base unitaria."""
        return self._tarifa_base

    # -------------------------------------------------------------------------
    # METODOS ABSTRACTOS OBLIGATORIOS (POLIMORFISMO)
    # -------------------------------------------------------------------------
    @abstractmethod
    def validar_parametros(self):
        """Valida los parametros especificos de cada servicio."""
        pass

    @abstractmethod
    def calcular_costo(self, impuesto: float = 0.19) -> float:
        """Calcula el costo total del servicio aplicando impuesto base."""
        pass

    @abstractmethod
    def describir_servicio(self) -> str:
        """Retorna una descripcion resumida del servicio."""
        pass

    def obtener_detalle(self) -> dict:
        """Implementacion del metodo abstracto heredado de EntidadBase."""
        return {
            "codigo": self.codigo_servicio,
            "nombre": self.nombre,
            "tarifa_base": self.tarifa_base,
            "tipo_servicio": self.__class__.__name__
        }


# =============================================================================
# SUBCLASE 1: RESERVA DE SALAS DE JUNTAS Y EVENTOS
# =============================================================================

class ReservaSala(Servicio):
    """
    Gestiona la reserva de salas ejecutivas, conferencias y talleres.
    Calcula el costo por horas, proyector y refrigerios.
    """

    def __init__(self, codigo_servicio: str, nombre: str, tarifa_base_hora: float,
                 capacidad_maxima: int, horas: int, incluye_proyector: bool = False,
                 incluye_refrigerio: bool = False):
        super().__init__(codigo_servicio, nombre, tarifa_base_hora)
        self.capacidad_maxima = capacidad_maxima
        self.horas = horas
        self.incluye_proyector = bool(incluye_proyector)
        self.incluye_refrigerio = bool(incluye_refrigerio)

        self.validar_parametros()

    def validar_parametros(self):
        """Valida que horas y capacidad sean valores positivos."""
        if self.horas <= 0:
            raise ParametroInvalidoError("Las horas de reserva deben ser mayores a cero.")
        if self.capacidad_maxima <= 0:
            raise ParametroInvalidoError("La capacidad maxima de la sala debe ser mayor a cero.")

    def calcular_costo(self, impuesto: float = 0.19) -> float:
        """Calcula el costo base de la sala mas adicionales e IVA."""
        subtotal = self.tarifa_base * self.horas

        if self.incluye_proyector:
            subtotal += 25000.0
        if self.incluye_refrigerio:
            subtotal += 15000.0 * self.capacidad_maxima

        return subtotal * (1.0 + impuesto)

    def describir_servicio(self) -> str:
        return f"Sala: {self.nombre} | Capacidad: {self.capacidad_maxima} pers | Horas: {self.horas}"


# =============================================================================
# SUBCLASE 2: ALQUILER DE EQUIPOS TECNOLOGICOS
# =============================================================================

class AlquilerEquipo(Servicio):
    """
    Gestiona el arrendamiento de equipos tecnologicos.
    Calcula el costo segun dias, cantidad y cobertura de seguro.
    """

    TIPOS_PERMITIDOS = ["Laptop", "Servidor", "Workstation", "Proyector"]

    def __init__(self, codigo_servicio: str, nombre: str, tarifa_diaria: float,
                 tipo_equipo: str, dias: int, cantidad: int, incluye_seguro: bool = True):
        super().__init__(codigo_servicio, nombre, tarifa_diaria)
        self.tipo_equipo = str(tipo_equipo).strip()
        self.dias = dias
        self.cantidad = cantidad
        self.incluye_seguro = bool(incluye_seguro)

        self.validar_parametros()

    def validar_parametros(self):
        """Valida tipo de equipo, dias y cantidad."""
        if self.tipo_equipo not in self.TIPOS_PERMITIDOS:
            raise ParametroInvalidoError(f"Tipo de equipo '{self.tipo_equipo}' no permitido.")
        if self.dias <= 0:
            raise ParametroInvalidoError("Los dias de alquiler deben ser mayores a cero.")
        if self.cantidad <= 0:
            raise ParametroInvalidoError("La cantidad de equipos debe ser mayor a cero.")

    def calcular_costo(self, impuesto: float = 0.19) -> float:
        """Calcula el costo del alquiler con seguro e IVA."""
        subtotal = self.tarifa_base * self.dias * self.cantidad

        if self.incluye_seguro:
            subtotal += subtotal * 0.10

        return subtotal * (1.0 + impuesto)

    def describir_servicio(self) -> str:
        return f"Alquiler: {self.nombre} | Tipo: {self.tipo_equipo} | Cant: {self.cantidad} | Dias: {self.dias}"
