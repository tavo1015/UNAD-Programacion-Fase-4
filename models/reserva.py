# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programacion (Codigo: 213023)
# Fase 4 - Practicas Simuladas (Software FJ)
# Modulo: Gestion de Reservas - Desarrollador 4
# Gestiona clientes, servicios, duracion y estados con excepciones y logs.

from datetime import datetime
from enum import Enum
from math import isfinite

from core.base import EntidadBase
from core.exceptions import (
    EstadoReservaInvalidoError,
    ReservaError,
    OperacionNoPermitidaError,
)
from core.logger import registrar_info, registrar_advertencia, registrar_error
from models.cliente import Cliente
from models.servicios import Servicio


class EstadoReserva(Enum):
    """Estados posibles de una reserva."""

    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    PROCESADA = "PROCESADA"


class Reserva(EntidadBase):
    """Reserva de un cliente para un servicio de Software FJ.

    Contrato de integracion con el equipo:
    - Cliente: propiedades nombre, cedula y es_vip.
    - Servicio: propiedad nombre y metodo calcular_costo(descuento=..., duracion=..., **kwargs).
      'duracion' se expresa en unidades acordadas con cada servicio (p. ej. horas).
    - EntidadBase: constructor id_entidad y propiedad id_entidad/_id_entidad.

    La duracion es obligatoria para reservas nuevas. Se mantiene `notas` como
    quinto argumento posicional para evitar romper llamadas previas.
    """

    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio,
                 fecha_evento: str, notas: str = "", *, duracion: float = 1.0):
        super().__init__(id_entidad=id_reserva)
        try:
            if not isinstance(cliente, Cliente):
                raise ReservaError("El cliente debe ser una instancia valida de Cliente.")
            if not isinstance(servicio, Servicio):
                raise ReservaError("El servicio debe ser una instancia valida de Servicio.")

            fecha_validada = self._validar_fecha_evento(fecha_evento)
            duracion_validada = self._validar_duracion(duracion)
            if notas is not None and not isinstance(notas, str):
                raise ReservaError("Las notas deben ser texto o None.")
        except ReservaError as error:
            registrar_error(f"No se pudo crear la reserva [{id_reserva}]", error)
            raise
        else:
            self._cliente = cliente
            self._servicio = servicio
            self._fecha_evento = fecha_validada
            self._duracion = duracion_validada
            self._notas = (notas or "").strip()
            self._estado = EstadoReserva.PENDIENTE
            self._costo_total = 0.0
            registrar_info(
                f"Reserva [{self.id_reserva}] creada en estado PENDIENTE "
                f"para el cliente {self._cliente.nombre}."
            )

    @staticmethod
    def _validar_duracion(duracion: float) -> float:
        """La duracion debe ser numerica, finita y mayor que cero."""
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)):
            raise ReservaError("La duracion debe ser un numero positivo.")
        valor = float(duracion)
        if not isfinite(valor) or valor <= 0:
            raise ReservaError("La duracion debe ser finita y mayor que cero.")
        return valor

    @staticmethod
    def _validar_descuento(descuento: float) -> float:
        """Descuentos expresados como proporcion: 0.10 equivale a 10 %."""
        if isinstance(descuento, bool) or not isinstance(descuento, (int, float)):
            raise ReservaError("El descuento debe ser un numero entre 0 y 1.")
        valor = float(descuento)
        if not isfinite(valor) or not 0 <= valor <= 1:
            raise ReservaError("El descuento debe estar entre 0 y 1 (0 % a 100 %).")
        return valor

    @staticmethod
    def _validar_fecha_evento(fecha_str: str) -> str:
        """Acepta fechas reales en AAAA-MM-DD o DD/MM/AAAA, con hora opcional."""
        if not isinstance(fecha_str, str) or not fecha_str.strip():
            raise ReservaError("La fecha del evento es obligatoria y debe ser texto.")

        cadena = fecha_str.strip()
        formatos = (
            "%Y-%m-%d %H:%M", "%Y-%m-%d",
            "%d/%m/%Y %H:%M", "%d/%m/%Y",
        )
        fecha_dt = None
        for formato in formatos:
            try:
                fecha_dt = datetime.strptime(cadena, formato)
                break
            except ValueError:
                continue
        if fecha_dt is None:
            raise ReservaError(
                f"La fecha '{fecha_str}' es invalida. Ejemplo: 2026-11-20 09:00."
            )

        # Regla de negocio original del proyecto, sujeta a acuerdo del equipo.
        if not 2024 <= fecha_dt.year <= 2035:
            raise ReservaError(
                f"El año {fecha_dt.year} esta fuera del rango operativo (2024-2035)."
            )
        return fecha_dt.strftime("%Y-%m-%d %H:%M")

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

    @property
    def duracion(self) -> float:
        return self._duracion

    @property
    def notas(self) -> str:
        return self._notas

    def confirmar(self, descuento_adicional: float = 0.0, **kwargs) -> float:
        """Calcula el costo y confirma solo si esta pendiente.

        El servicio debe admitir `duracion` y `descuento` como argumentos.
        No se cambia el estado si el calculo produce un error.
        """
        operacion_exitosa = False
        try:
            if self._estado != EstadoReserva.PENDIENTE:
                raise EstadoReservaInvalidoError(
                    f"No se puede confirmar [{self.id_reserva}] en estado {self._estado.value}; "
                    "debe estar PENDIENTE."
                )

            if "descuento" in kwargs or "duracion" in kwargs:
                raise ReservaError(
                    "Use descuento_adicional y la duracion de la reserva; "
                    "no pase descuento/duracion en kwargs."
                )

            adicional = self._validar_descuento(descuento_adicional)
            es_vip = self._cliente.es_vip
            if not isinstance(es_vip, bool):
                raise ReservaError("La propiedad es_vip del cliente debe ser booleana.")
            descuento_total = adicional + (0.10 if es_vip else 0.0)
            if descuento_total > 1:
                raise ReservaError(
                    "El descuento total (incluido VIP) no puede superar el 100 %."
                )

            costo = self._servicio.calcular_costo(
                duracion=self._duracion, descuento=descuento_total, **kwargs
            )
            if isinstance(costo, bool) or not isinstance(costo, (int, float)):
                raise ReservaError("El costo calculado debe ser un numero.")
            if not isfinite(float(costo)) or costo < 0:
                raise ReservaError("El costo calculado no puede ser negativo o infinito.")

            self._costo_total = float(costo)
            self._estado = EstadoReserva.CONFIRMADA
            operacion_exitosa = True
        except (EstadoReservaInvalidoError, ReservaError) as error:
            registrar_error(f"Fallo al confirmar reserva [{self.id_reserva}]", error)
            raise
        except Exception as error:
            mensaje = f"Error al calcular costo de reserva [{self.id_reserva}]"
            registrar_error(mensaje, error)
            raise ReservaError(mensaje) from error
        else:
            registrar_info(
                f"Reserva [{self.id_reserva}] confirmada. "
                f"Costo: ${self._costo_total:,.2f}"
            )
            return self._costo_total
        finally:
            resultado = "EXITOSA" if operacion_exitosa else "FALLIDA"
            registrar_info(
                f"[AUDITORIA] Confirmacion [{self.id_reserva}]: {resultado}"
            )

    def cancelar(self, motivo: str = "Solicitud del cliente") -> None:
        """Cancela una reserva pendiente o confirmada, nunca procesada."""
        try:
            if self._estado == EstadoReserva.CANCELADA:
                raise EstadoReservaInvalidoError(
                    f"La reserva [{self.id_reserva}] ya esta CANCELADA."
                )
            if self._estado == EstadoReserva.PROCESADA:
                raise OperacionNoPermitidaError(
                    f"La reserva [{self.id_reserva}] ya fue PROCESADA."
                )
            if not isinstance(motivo, str) or not motivo.strip():
                raise ReservaError("El motivo de cancelacion debe ser texto no vacio.")

            self._estado = EstadoReserva.CANCELADA
            registrar_advertencia(
                f"Reserva [{self.id_reserva}] CANCELADA. Motivo: {motivo.strip()}"
            )
        except (EstadoReservaInvalidoError, OperacionNoPermitidaError, ReservaError) as error:
            registrar_error(f"Fallo en cancelacion [{self.id_reserva}]", error)
            raise

    def procesar(self) -> None:
        """Procesa solo reservas previamente confirmadas."""
        if self._estado != EstadoReserva.CONFIRMADA:
            error = EstadoReservaInvalidoError(
                f"No se puede procesar [{self.id_reserva}] en estado {self._estado.value}; "
                "debe estar CONFIRMADA."
            )
            registrar_error(f"Fallo al procesar [{self.id_reserva}]", error)
            raise error
        self._estado = EstadoReserva.PROCESADA
        registrar_info(f"Reserva [{self.id_reserva}] PROCESADA exitosamente.")

    def obtener_detalle(self) -> dict:
        return {
            "id_reserva": self.id_reserva,
            "cliente": self.cliente.nombre,
            "cedula": self.cliente.cedula,
            "servicio": self.servicio.nombre,
            "fecha_evento": self.fecha_evento,
            "duracion": self.duracion,
            "notas": self.notas,
            "estado": self.estado.value,
            "costo_total": self.costo_total,
        }

    def __str__(self) -> str:
        return (
            f"Reserva #{self.id_reserva} | Cliente: {self._cliente.nombre} | "
            f"Servicio: {self._servicio.nombre} | Fecha: {self._fecha_evento} | "
            f"Duracion: {self._duracion:g} | Estado: {self._estado.value} | "
            f"Total: ${self._costo_total:,.2f}"
        )
