# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programacion (Codigo: 213023)
# Fase 4 - Practicas Simuladas (Software FJ)
# Modulo: Servicios Especializados
# Descripcion: Implementa la clase abstracta Servicio y tres servicios especializados:
# 1. ReservaSala, 2. AlquilerEquipo, 3. AsesoriaEspecializada.
# Incorpora sobrecarga de metodos y registro de eventos en el logger del sistema.

from abc import abstractmethod
from core.base import EntidadBase
from core.exceptions import ParametroInvalidoError
from core.logger import registrar_info


# =============================================================================
# CLASE ABSTRACTA: SERVICIO
# =============================================================================

class Servicio(EntidadBase):
    """
    Clase abstracta que modela cualquier servicio ofrecido por Software FJ.
    Define el contrato obligatorio para validar_parametros(), calcular_costo()
    y describir_servicio().
    """

    def __init__(self, codigo_servicio: str, nombre: str, tarifa_base: float):
        super().__init__(id_entidad=codigo_servicio)

        if not nombre or len(str(nombre).strip()) < 3:
            raise ParametroInvalidoError("El nombre del servicio debe contener al menos 3 caracteres.")

        if not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            raise ParametroInvalidoError("La tarifa base del servicio debe ser un valor positivo mayor a cero.")

        self._codigo_servicio = str(codigo_servicio).strip().upper()
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
        """Valida que los parametros particulares del servicio sean consistentes."""
        pass

    @abstractmethod
    def calcular_costo(self, descuento: float = 0.0, impuesto: float = 0.19, **kwargs) -> float:
        """Calcula el costo final con descuentos, impuestos y parametros opcionales."""
        pass

    @abstractmethod
    def describir_servicio(self) -> str:
        """Retorna una descripcion detallada del servicio."""
        pass

    def obtener_detalle(self) -> dict:
        """Implementacion del metodo abstracto de EntidadBase."""
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
    Incorpora sobrecarga de parametros para horas extra y descuentos.
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
        registrar_info(f"Servicio de Sala '{self.nombre}' configurado correctamente.")

    def validar_parametros(self):
        """Valida que horas y capacidad sean positivos."""
        if self.horas <= 0:
            raise ParametroInvalidoError(f"Las horas de sala ({self.horas}) deben ser un entero positivo.")
        if self.capacidad_maxima <= 0:
            raise ParametroInvalidoError(f"La capacidad maxima ({self.capacidad_maxima}) debe ser mayor a cero.")

    def calcular_costo(self, descuento: float = 0.0, impuesto: float = 0.19, horas_extra: int = 0) -> float:
        """Calcula el costo total de la sala aplicando horas extra, descuento e IVA."""
        if horas_extra < 0:
            raise ParametroInvalidoError("Las horas extra no pueden ser negativas.")

        total_horas = self.horas + horas_extra
        subtotal = self.tarifa_base * total_horas

        if self.incluye_proyector:
            subtotal += 25000.0
        if self.incluye_refrigerio:
            subtotal += (15000.0 * self.capacidad_maxima)

        subtotal_con_descuento = subtotal * (1.0 - descuento)
        costo_final = subtotal_con_descuento * (1.0 + impuesto)
        return round(costo_final, 2)

    def describir_servicio(self) -> str:
        proy = "Si" if self.incluye_proyector else "No"
        refr = "Si" if self.incluye_refrigerio else "No"
        return (f"Sala: {self.nombre} | Capacidad: {self.capacidad_maxima} pers | "
                f"Horas: {self.horas} | Proyector: {proy} | Refrigerio: {refr}")


# =============================================================================
# SUBCLASE 2: ALQUILER DE EQUIPOS TECNOLOGICOS
# =============================================================================

class AlquilerEquipo(Servicio):
    """
    Gestiona el arrendamiento de equipos tecnologicos.
    Incorpora recargo por entrega express mediante sobrecarga de metodos.
    """

    TIPOS_PERMITIDOS = ["Laptop", "Servidor", "Workstation", "Proyector"]

    def __init__(self, codigo_servicio: str, nombre: str, tarifa_diaria: float,
                 tipo_equipo: str, dias: int, cantidad: int, incluye_seguro: bool = True):
        super().__init__(codigo_servicio, nombre, tarifa_diaria)
        self.tipo_equipo = str(tipo_equipo).strip().title()
        self.dias = dias
        self.cantidad = cantidad
        self.incluye_seguro = bool(incluye_seguro)

        self.validar_parametros()
        registrar_info(f"Servicio de Alquiler '{self.nombre}' ({self.tipo_equipo}) configurado.")

    def validar_parametros(self):
        """Valida tipo de equipo, dias y cantidad."""
        if self.tipo_equipo not in self.TIPOS_PERMITIDOS:
            raise ParametroInvalidoError(
                f"Tipo de equipo '{self.tipo_equipo}' no reconocido. Permitidos: {', '.join(self.TIPOS_PERMITIDOS)}"
            )
        if self.dias <= 0:
            raise ParametroInvalidoError(f"Los dias de alquiler ({self.dias}) deben ser mayores a cero.")
        if self.cantidad <= 0:
            raise ParametroInvalidoError(f"La cantidad de equipos ({self.cantidad}) debe ser mayor a cero.")

    def calcular_costo(self, descuento: float = 0.0, impuesto: float = 0.19, entrega_express: bool = False) -> float:
        """Calcula el valor del alquiler con seguro, entrega express, descuento e IVA."""
        subtotal = self.tarifa_base * self.dias * self.cantidad

        if self.incluye_seguro:
            subtotal += (subtotal * 0.10)

        if entrega_express:
            subtotal += 40000.0

        subtotal_con_descuento = subtotal * (1.0 - descuento)
        costo_final = subtotal_con_descuento * (1.0 + impuesto)
        return round(costo_final, 2)

    def describir_servicio(self) -> str:
        seguro = "Si" if self.incluye_seguro else "No"
        return (f"Alquiler: {self.nombre} | Tipo: {self.tipo_equipo} | "
                f"Cant: {self.cantidad} | Dias: {self.dias} | Seguro: {seguro}")


# =============================================================================
# SUBCLASE 3: ASESORIA ESPECIALIZADA
# =============================================================================

class AsesoriaEspecializada(Servicio):
    """
    Gestiona servicios de consultoria tecnica segun nivel del consultor y modalidad.
    """

    MULTIPLICADORES_NIVEL = {
        "Junior": 1.0,
        "Senior": 1.5,
        "Master": 2.0
    }

    def __init__(self, codigo_servicio: str, nombre: str, tarifa_hora_base: float,
                 area_especialidad: str, nivel_consultor: str, horas: int,
                 modalidad_presencial: bool = False):
        super().__init__(codigo_servicio, nombre, tarifa_hora_base)
        self.area_especialidad = str(area_especialidad).strip()
        self.nivel_consultor = str(nivel_consultor).strip().capitalize()
        self.horas = horas
        self.modalidad_presencial = bool(modalidad_presencial)

        self.validar_parametros()
        registrar_info(f"Asesoria '{self.nombre}' en {self.area_especialidad} configurada.")

    def validar_parametros(self):
        """Valida existencia del nivel de consultor y horas positivas."""
        if self.nivel_consultor not in self.MULTIPLICADORES_NIVEL:
            niveles = ", ".join(self.MULTIPLICADORES_NIVEL.keys())
            raise ParametroInvalidoError(
                f"Nivel de consultor '{self.nivel_consultor}' no valido. Disponibles: {niveles}"
            )
        if self.horas <= 0:
            raise ParametroInvalidoError(f"Las horas de asesoria ({self.horas}) deben ser mayores a cero.")

    def calcular_costo(self, descuento: float = 0.0, impuesto: float = 0.19, sesion_urgente: bool = False) -> float:
        """Calcula la tarifa segun nivel del consultor, viaticos y recargo por urgencia."""
        factor_nivel = self.MULTIPLICADORES_NIVEL[self.nivel_consultor]
        subtotal = (self.tarifa_base * factor_nivel) * self.horas

        if self.modalidad_presencial:
            subtotal += 50000.0

        if sesion_urgente:
            subtotal += (subtotal * 0.25)

        subtotal_con_descuento = subtotal * (1.0 - descuento)
        costo_final = subtotal_con_descuento * (1.0 + impuesto)
        return round(costo_final, 2)

    def describir_servicio(self) -> str:
        mod = "Presencial" if self.modalidad_presencial else "Remota"
        return (f"Asesoria: {self.nombre} | Area: {self.area_especialidad} | "
                f"Nivel: {self.nivel_consultor} | Horas: {self.horas} | Modalidad: {mod}")
