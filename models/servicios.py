# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programacion (Codigo: 213023)
# Fase 4 - Practicas Simuladas (Software FJ)
# Modulo: Servicios Especializados
# Descripcion: Implementa la clase abstracta Servicio y tres servicios especializados:
# 1. ReservaSala, 2. AlquilerEquipo, 3. AsesoriaEspecializada.
# Aplica principios de Abstraccion, Herencia, Polimorfismo y Sobrecarga de metodos.

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
    Define el contrato obligatorio para los metodos polimorficos:
    calcular_costo(), describir_servicio() y validar_parametros().
    """

    def __init__(self, codigo_servicio: str, nombre: str, tarifa_base: float):
        # Invocacion a la clase abstracta base con el codigo como id unico
        super().__init__(id_entidad=codigo_servicio)

        # Validacion del nombre del servicio
        if not nombre or len(str(nombre).strip()) < 3:
            raise ParametroInvalidoError("El nombre del servicio debe contener al menos 3 caracteres.")

        # Validacion de tarifa base no negativa y rango realista comercial
        if not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            raise ParametroInvalidoError("La tarifa base del servicio debe ser un valor positivo mayor a cero.")
        if tarifa_base > 50000000.0:  # Limite de 50 millones COP
            raise ParametroInvalidoError(
                f"La tarifa base (${tarifa_base:,.2f} COP) excede el limite maximo comercial permitido ($50,000,000 COP)."
            )

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
        """Valida que los parametros particulares de la especialidad sean consistentes."""
        pass

    @abstractmethod
    def calcular_costo(self, descuento: float = 0.0, impuesto: float = 0.19, **kwargs) -> float:
        """
        Metodo polimorfico sobrecargado mediante argumentos nombrados y opcionales
        para calcular el costo final con descuentos e impuestos.
        """
        pass

    @abstractmethod
    def describir_servicio(self) -> str:
        """Retorna una descripcion detallada y estructurada del servicio."""
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
    Sobrescribe el calculo de costos incorporando horas, proyector y refrigerios.
    """

    def __init__(self, codigo_servicio: str, nombre: str, tarifa_base_hora: float,
                 capacidad_maxima: int, horas: int, incluye_proyector: bool = False,
                 incluye_refrigerio: bool = False):
        super().__init__(codigo_servicio, nombre, tarifa_base_hora)
        self.capacidad_maxima = capacidad_maxima
        self.horas = horas
        self.incluye_proyector = bool(incluye_proyector)
        self.incluye_refrigerio = bool(incluye_refrigerio)

        # Validacion inmediata al instanciar
        self.validar_parametros()
        registrar_info(f"Servicio de Sala '{self.nombre}' configurado correctamente.")

    def validar_parametros(self):
        """Valida horas y capacidad dentro de limites realistas de aforo y horario."""
        if not isinstance(self.horas, int) or self.horas <= 0:
            raise ParametroInvalidoError(f"Las horas de sala ({self.horas}) deben ser un entero positivo.")
        if self.horas > 72:
            raise ParametroInvalidoError(f"Las horas de sala ({self.horas}) no pueden exceder 72 horas continuas (3 dias).")
        if not isinstance(self.capacidad_maxima, int) or self.capacidad_maxima <= 0:
            raise ParametroInvalidoError(f"La capacidad maxima ({self.capacidad_maxima}) debe ser mayor a cero.")
        if self.capacidad_maxima > 500:
            raise ParametroInvalidoError(
                f"La capacidad de la sala ({self.capacidad_maxima} personas) excede el aforo maximo comercial de 500 personas."
            )

    # Sobrecarga con parametros opcionales: horas_extra
    def calcular_costo(self, descuento: float = 0.0, impuesto: float = 0.19, horas_extra: int = 0) -> float:
        """
        Calcula el costo total de la sala aplicando sobrecarga de parametros.
        Permite extender horas con costo adicional y aplicar descuentos e IVA.
        """
        if horas_extra < 0:
            raise ParametroInvalidoError("Las horas extra no pueden ser negativas.")
        if horas_extra > 24:
            raise ParametroInvalidoError(f"Las horas extra ({horas_extra}) no pueden superar 24 horas por evento.")

        total_horas = self.horas + horas_extra
        subtotal = self.tarifa_base * total_horas

        # Adicionales de sala
        if self.incluye_proyector:
            subtotal += 25000.0  # Costo fijo de proyector
        if self.incluye_refrigerio:
            subtotal += (15000.0 * self.capacidad_maxima)  # Costo por persona

        # Aplicacion de descuento (validado entre 0 y 1)
        descuento_aplicado = min(max(descuento, 0.0), 1.0)
        subtotal_con_descuento = subtotal * (1.0 - descuento_aplicado)

        # Aplicacion de impuesto (IVA)
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
    Gestiona el arrendamiento de computadores portatiles, servidores o estaciones.
    Sobrescribe el calculo de costos segun dias, cantidad y cobertura de seguro.
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
        """Valida que los dias y la cantidad sean mayores a cero y el tipo sea reconocido."""
        if self.tipo_equipo not in self.TIPOS_PERMITIDOS:
            raise ParametroInvalidoError(
                f"Tipo de equipo '{self.tipo_equipo}' no reconocido. Permitidos: {', '.join(self.TIPOS_PERMITIDOS)}"
            )
        if not isinstance(self.dias, int) or self.dias <= 0:
            raise ParametroInvalidoError(f"Los dias de alquiler ({self.dias}) deben ser mayores a cero.")
        if self.dias > 365:
            raise ParametroInvalidoError(f"El periodo de alquiler ({self.dias} dias) no puede superar 365 dias (1 año).")
        if not isinstance(self.cantidad, int) or self.cantidad <= 0:
            raise ParametroInvalidoError(f"La cantidad de equipos ({self.cantidad}) debe ser mayor a cero.")
        if self.cantidad > 200:
            raise ParametroInvalidoError(
                f"La cantidad de equipos solicitada ({self.cantidad}) excede el inventario maximo disponible (200 unidades)."
            )

    # Sobrecarga con parametros opcionales: entrega_express
    def calcular_costo(self, descuento: float = 0.0, impuesto: float = 0.19, entrega_express: bool = False) -> float:
        """
        Calcula el valor del alquiler considerando dias, seguro y logistica express.
        """
        subtotal = self.tarifa_base * self.dias * self.cantidad

        # Seguro contra daños y robo (10% sobre la base de alquiler)
        if self.incluye_seguro:
            subtotal += (subtotal * 0.10)

        # Recargo por logistica de entrega express el mismo dia
        if entrega_express:
            subtotal += 40000.0

        # Descuentos e impuestos
        descuento_aplicado = min(max(descuento, 0.0), 1.0)
        subtotal_con_descuento = subtotal * (1.0 - descuento_aplicado)
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
    Gestiona servicios de consultoria tecnica (Ciberseguridad, Cloud, DevOps, IA).
    Sobrescribe el calculo segun nivel del consultor y modalidad.
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
        if not isinstance(self.horas, int) or self.horas <= 0:
            raise ParametroInvalidoError(f"Las horas de asesoria ({self.horas}) deben ser mayores a cero.")
        if self.horas > 240:
            raise ParametroInvalidoError(
                f"Las horas de consultoria ({self.horas}) exceden el cupo maximo mensual permitido de 240 horas."
            )

    # Sobrecarga con parametros opcionales: sesion_urgente
    def calcular_costo(self, descuento: float = 0.0, impuesto: float = 0.19, sesion_urgente: bool = False) -> float:
        """
        Calcula la tarifa considerando la jerarquia del consultor y desplazamiento.
        """
        factor_nivel = self.MULTIPLICADORES_NIVEL[self.nivel_consultor]
        tarifa_real_hora = self.tarifa_base * factor_nivel
        subtotal = tarifa_real_hora * self.horas

        # Viaticos de traslado si es presencial
        if self.modalidad_presencial:
            subtotal += 50000.0

        # Recargo por atencion fuera de horario laboral / urgente
        if sesion_urgente:
            subtotal += (subtotal * 0.25)

        descuento_aplicado = min(max(descuento, 0.0), 1.0)
        subtotal_con_descuento = subtotal * (1.0 - descuento_aplicado)
        costo_final = subtotal_con_descuento * (1.0 + impuesto)
        return round(costo_final, 2)

    def describir_servicio(self) -> str:
        mod = "Presencial" if self.modalidad_presencial else "Remota"
        return (f"Asesoria: {self.nombre} | Area: {self.area_especialidad} | "
                f"Nivel: {self.nivel_consultor} | Horas: {self.horas} | Modalidad: {mod}")
