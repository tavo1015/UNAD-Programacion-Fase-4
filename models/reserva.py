# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programacion (Codigo: 213023)
# Fase 4 - Practicas Simuladas (Software FJ)
# Modulo: Gestion de Reservas
# Descripcion: Implementa la clase Reserva y el enum de estados, articulando
# clientes y servicios con control de transiciones y manejo riguroso de excepciones.

from enum import Enum
from datetime import datetime
from core.base import EntidadBase
from core.exceptions import (
    EstadoReservaInvalidoError,
    ReservaError,
    OperacionNoPermitidaError
)
from core.logger import registrar_info, registrar_advertencia, registrar_error
from models.cliente import Cliente
from models.servicios import Servicio


class EstadoReserva(Enum):
    """Enumeracion de los posibles estados en el ciclo de vida de una reserva."""
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    PROCESADA = "PROCESADA"


class Reserva(EntidadBase):
    """
    Representa una reserva de servicio contratada por un cliente en Software FJ.
    Maneja el ciclo de vida (confirmacion, cancelacion y procesamiento)
    utilizando bloques try/except/else/finally y encadenamiento de excepciones.
    """

    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio,
                 fecha_evento: str, notas: str = ""):
        super().__init__(id_entidad=id_reserva)

        # Validacion estricta de tipos de objetos vinculados
        if not isinstance(cliente, Cliente):
            raise TypeError("El cliente vinculado a la reserva debe ser una instancia valida de Cliente.")
        if not isinstance(servicio, Servicio):
            raise TypeError("El servicio vinculado debe ser una instancia valida de Servicio.")

        self._cliente = cliente
        self._servicio = servicio
        self._fecha_evento = self._validar_fecha_evento(fecha_evento)
        self._notas = str(notas).strip()
        self._estado = EstadoReserva.PENDIENTE
        self._costo_total = 0.0

        registrar_info(
            f"Reserva [{self.id_entidad}] creada en estado PENDIENTE para el cliente {self._cliente.nombre}."
        )

    @staticmethod
    def _validar_fecha_evento(fecha_str: str) -> str:
        """
        Valida que la fecha del evento cumpla un formato de calendario valido
        (AAAA-MM-DD o AAAA-MM-DD HH:MM) y corresponda a una fecha real y coherente.
        Rechaza textos arbitrarios o fechas inexistentes (ej: 30 de febrero).
        """
        cadena = str(fecha_str).strip()
        if not cadena:
            raise ReservaError("La fecha del evento es obligatoria y no puede estar vacia.")

        formatos = [
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y"
        ]

        fecha_dt = None
        for fmt in formatos:
            try:
                fecha_dt = datetime.strptime(cadena, fmt)
                break
            except ValueError:
                continue

        if not fecha_dt:
            raise ReservaError(
                f"La fecha '{fecha_str}' es invalida. Debe ingresar una fecha valida "
                "en formato AAAA-MM-DD o AAAA-MM-DD HH:MM (ejemplo: 2026-11-20 09:00)."
            )

        # Validacion de rango de años operativos
        if not (2024 <= fecha_dt.year <= 2035):
            raise ReservaError(
                f"El año {fecha_dt.year} de la fecha ingresada esta fuera del rango operativo de Software FJ (2024-2035)."
            )

        return fecha_dt.strftime("%Y-%m-%d %H:%M")

    # -------------------------------------------------------------------------
    # PROPIEDADES ENCAPSULADAS
    # -------------------------------------------------------------------------
    @property
    def id_reserva(self) -> str:
        return self._id_entidad

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def costo_total(self) -> float:
        return self._costo_total

    @property
    def fecha_evento(self) -> str:
        return self._fecha_evento

    # -------------------------------------------------------------------------
    # METODOS DE NEGOCIO CON CONTROL DE EXCEPCIONES
    # -------------------------------------------------------------------------
    def confirmar(self, descuento_adicional: float = 0.0, **kwargs) -> float:
        """
        Confirma la reserva calculando el costo total definitivo.
        Implementa el bloque try / except / else / finally exigido en la guia.
        """
        operacion_exitosa = False
        try:
            # Validacion de estado: Solo reservas PENDIENTES pueden confirmarse
            if self._estado == EstadoReserva.CANCELADA:
                raise EstadoReservaInvalidoError(
                    f"No es posible confirmar la reserva [{self.id_reserva}] porque se encuentra CANCELADA."
                )
            if self._estado == EstadoReserva.CONFIRMADA:
                raise EstadoReservaInvalidoError(
                    f"La reserva [{self.id_reserva}] ya ha sido previamente CONFIRMADA."
                )

            # Si el cliente es VIP, se le otorga un 10% adicional de descuento
            descuento_total = descuento_adicional
            if self._cliente.es_vip:
                descuento_total += 0.10

            # Calculo polimorfico del costo segun el tipo de servicio contratado
            self._costo_total = self._servicio.calcular_costo(descuento=descuento_total, **kwargs)
            self._estado = EstadoReserva.CONFIRMADA
            operacion_exitosa = True

        except EstadoReservaInvalidoError as err:
            registrar_error(f"Fallo al confirmar reserva [{self.id_reserva}]", err)
            raise err

        except Exception as err_inesperado:
            # Encadenamiento de excepciones (raise ... from ...)
            mensaje = f"Error critico al calcular costos para reserva [{self.id_reserva}]: {str(err_inesperado)}"
            registrar_error(mensaje, err_inesperado)
            raise ReservaError(mensaje) from err_inesperado

        else:
            # El bloque ELSE solo se ejecuta si NO hubo ninguna excepcion
            registrar_info(
                f"Reserva [{self.id_reserva}] confirmada con exito. Costo liquidado: ${self._costo_total:,.2f}"
            )
            return self._costo_total

        finally:
            # El bloque FINALLY se ejecuta SIEMPRE para tareas de auditoria o cierre
            estado_desc = "EXITOSA" if operacion_exitosa else "FALLIDA"
            registrar_info(f"[AUDITORIA FINALLY] Fin de intento de confirmacion para [{self.id_reserva}]: {estado_desc}")

    def cancelar(self, motivo: str = "Solicitud del cliente"):
        """
        Cancela una reserva pendiente o confirmada.
        Dispara EstadoReservaInvalidoError si ya estaba cancelada o procesada.
        """
        try:
            if self._estado == EstadoReserva.CANCELADA:
                raise EstadoReservaInvalidoError(
                    f"La reserva [{self.id_reserva}] ya esta CANCELADA. Operacion redundante rechazada."
                )
            if self._estado == EstadoReserva.PROCESADA:
                raise OperacionNoPermitidaError(
                    f"La reserva [{self.id_reserva}] ya fue PROCESADA y prestada; no se puede anular."
                )

            self._estado = EstadoReserva.CANCELADA
            registrar_advertencia(f"Reserva [{self.id_reserva}] ha sido CANCELADA. Motivo: {motivo}")

        except (EstadoReservaInvalidoError, OperacionNoPermitidaError) as e:
            registrar_error(f"Fallo en cancelacion de [{self.id_reserva}]", e)
            raise e

    def procesar(self):
        """
        Simula la ejecucion efectiva del servicio. Requiere que este CONFIRMADA.
        """
        if self._estado != EstadoReserva.CONFIRMADA:
            err = EstadoReservaInvalidoError(
                f"No se puede procesar la reserva [{self.id_reserva}] en estado '{self._estado.value}'. Debe estar CONFIRMADA."
            )
            registrar_error(f"Intento de procesar reserva no confirmada [{self.id_reserva}]", err)
            raise err

        self._estado = EstadoReserva.PROCESADA
        registrar_info(f"Reserva [{self.id_reserva}] procesada y culminada exitosamente.")

    def obtener_detalle(self) -> dict:
        return {
            "id_reserva": self.id_reserva,
            "cliente": self.cliente.nombre,
            "cedula": self.cliente.cedula,
            "servicio": self.servicio.nombre,
            "fecha_evento": self.fecha_evento,
            "estado": self.estado.value,
            "costo_total": self.costo_total
        }

    def __str__(self) -> str:
        return (f"Reserva #{self.id_reserva} | Cliente: {self._cliente.nombre} | "
                f"Servicio: {self._servicio.nombre} | Fecha: {self._fecha_evento} | "
                f"Estado: {self._estado.value} | Total: ${self._costo_total:,.2f}")

